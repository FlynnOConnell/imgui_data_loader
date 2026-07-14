"""Capture documentation screenshots of the example dialogs.

Mirrors mbo_utilities/scripts/capture_docs.py: each example's *real* dialog is
run in a hello_imgui window and its framebuffer is read back with
hello_imgui.final_app_window_screenshot(), then autocropped to the content and
given padding + a soft drop shadow. Images land under docs/_images/examples/.

Needs a desktop session (framebuffer screenshots require a real GL surface) plus
the docs extras:  pip install -e ".[docs]"  (pillow + numpy).

    python scripts/capture_docs.py            # capture everything
    python scripts/capture_docs.py --one 04_slots_options [--popup]   # one (worker)
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO / "examples"
OUTPUT_DIR = REPO / "docs" / "_images" / "examples"

EXAMPLES = [
    "01_minimal",
    "02_buttons_filetypes",
    "03_theme_info",
    "04_slots_options",
    "05_recent_files",
    "06_embedded_app",
]

# style_image knobs (matches the mbo_utilities docs treatment)
PADDING = 24
SHADOW_BLUR = 12
SHADOW_OFFSET = (0, 6)
SHADOW_OPACITY = 0.28


def style_image(img: Image.Image, output_path: Path) -> None:
    """Transparent padding + soft drop shadow, saved as PNG."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    margin = SHADOW_BLUR * 2
    out = Image.new("RGBA", (img.width + PADDING * 2, img.height + PADDING * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (img.width + margin, img.height + margin), (0, 0, 0, 0))
    core = Image.new("RGBA", (img.width, img.height), (0, 0, 0, int(255 * SHADOW_OPACITY)))
    shadow.paste(core, (margin // 2, margin // 2))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    out.paste(
        shadow,
        (PADDING + SHADOW_OFFSET[0] - margin // 2, PADDING + SHADOW_OFFSET[1] - margin // 2),
        shadow,
    )
    out.paste(img, (PADDING, PADDING))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, "PNG")
    print(f"  -> {output_path.relative_to(REPO)}")


def autocrop(arr: np.ndarray, margin: int = 10, tol: int = 18) -> np.ndarray:
    """Crop to the bounding box of pixels that differ from the corner (window
    background) color, leaving a small margin. Trims dead space around the
    dialog regardless of window size."""
    bg = arr[0, 0].astype(int)
    diff = np.abs(arr.astype(int) - bg).sum(axis=2)
    ys, xs = np.where(diff > tol)
    if len(ys) == 0:
        return arr
    y0 = max(0, int(ys.min()) - margin)
    x0 = max(0, int(xs.min()) - margin)
    y1 = min(arr.shape[0], int(ys.max()) + 1 + margin)
    x1 = min(arr.shape[1], int(xs.max()) + 1 + margin)
    return arr[y0:y1, x0:x1]


def _load_example(stem: str):
    spec = importlib.util.spec_from_file_location(f"_ex_{stem}", EXAMPLES_DIR / f"{stem}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _capture_one(stem: str, popup: bool = False) -> None:
    from imgui_bundle import hello_imgui, immapp

    from imgui_data_loader import FileDialog, ensure_assets

    mod = _load_example(stem)
    dlg = FileDialog(mod.build_config())
    size = getattr(mod, "WINDOW_SIZE", (360, 780))

    ensure_assets()
    frames = {"n": 0}

    def pre_new_frame():
        frames["n"] += 1
        if popup and frames["n"] == 4:
            dlg.open_options()
        if frames["n"] >= 12:
            hello_imgui.get_runner_params().app_shall_exit = True

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = stem
    params.app_window_params.window_geometry.size = tuple(size)
    params.app_window_params.window_geometry.size_auto = False
    params.app_window_params.restore_previous_geometry = False  # honor the size
    params.app_window_params.resizable = False
    params.fps_idling.enable_idling = False
    params.ini_folder_type = hello_imgui.IniFolderType.temp_folder
    params.ini_filename = f"idl_capture_{stem}.ini"
    params.callbacks.show_gui = dlg.render
    params.callbacks.pre_new_frame = pre_new_frame

    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    immapp.run(params, addons)

    shot = np.asarray(hello_imgui.final_app_window_screenshot())
    if shot.size == 0:
        print(f"  {stem}: empty screenshot buffer (need a desktop session)")
        return
    cropped = autocrop(shot[..., :3])
    name = f"{stem}_popup.png" if popup else f"{stem}.png"
    style_image(Image.fromarray(cropped), OUTPUT_DIR / name)


def _has_options(stem: str) -> bool:
    return getattr(_load_example(stem).build_config(), "options_draw", None) is not None


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stem in EXAMPLES:
        print(f"{stem} ...")
        # isolate each capture in a subprocess: fresh module + GL state per run
        subprocess.run([sys.executable, str(Path(__file__).resolve()), "--one", stem], check=False)
        if _has_options(stem):
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--one", stem, "--popup"],
                check=False,
            )


if __name__ == "__main__":
    if "--one" in sys.argv:
        i = sys.argv.index("--one")
        _capture_one(sys.argv[i + 1], popup="--popup" in sys.argv)
    else:
        main()
