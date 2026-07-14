"""02 - Everything: one config that uses every feature at once.

Branding, custom `buttons` covering every `PickKind` with their own filters, a
custom `Theme`, a `top_draw` row above the buttons, an `info` card, an Options
popup, recent-files persistence, and result callbacks. Each imgui widget returns
`(changed, new_value)` - keep the value.

    python examples/02_everything.py
"""

from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui

from imgui_data_loader import (
    ButtonSpec,
    DialogResult,
    FileDialogConfig,
    FileType,
    JsonPreferenceStore,
    PickKind,
    Theme,
    center_text,
    run_file_dialog,
)

WINDOW_SIZE = (360, 640)

STORE = JsonPreferenceStore()  # ~/.config/imgui_data_loader/recent.json
STATE = {"mode": 0, "recurse": True, "downsample": 1}
MODES = ["2D", "3D volume", "Time series"]
IMAGES = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]


def mode_row(dlg) -> None:  # top_draw: a widget row between header and buttons
    imgui.set_next_item_width(imgui.get_content_region_avail().x)
    _, STATE["mode"] = imgui.combo("##mode", STATE["mode"], MODES)


def info(dlg) -> None:  # info card contents
    center_text("Supported formats", dlg.theme.accent)
    imgui.bullet_text("TIFF / Zarr / HDF5")
    recent = STORE.recent()
    if recent:
        imgui.text_colored(dlg.theme.text_dim, "Recent:")
        for path in recent[:3]:
            imgui.bullet_text(path)


def options(dlg) -> None:  # options_draw: the popup body
    _, STATE["recurse"] = imgui.checkbox("Recurse into subfolders", STATE["recurse"])
    imgui.set_next_item_width(140)
    _, STATE["downsample"] = imgui.slider_int("Downsample", STATE["downsample"], 1, 8)


def on_select(result: DialogResult) -> None:
    print(f"mode={MODES[STATE['mode']]} recurse={STATE['recurse']} "
          f"downsample={STATE['downsample']}")
    print("selected:", result.paths)


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Volume Loader",
        subtitle="every feature at once",
        theme=Theme.dark().replace(accent=(0.20, 0.75, 0.70, 1.0)),
        default_dir="",                 # persistence seeds this instead
        persistence=STORE,              # seeds start dir + records selections
        top_draw=mode_row,
        info=info,
        options_draw=options,
        options_label="Load options",
        quit_label="Close",
        on_select=on_select,
        on_cancel=lambda: print("cancelled"),
        buttons=[
            ButtonSpec("Open image(s)", PickKind.OPEN_FILE, icon=fa.ICON_FA_FILE_IMAGE,
                       multiselect=True, filetypes=IMAGES),
            ButtonSpec("Open a folder", PickKind.SELECT_FOLDER, icon=fa.ICON_FA_FOLDER_OPEN),
            ButtonSpec("Export as…", PickKind.SAVE_FILE, icon=fa.ICON_FA_FLOPPY_DISK,
                       filetypes=[FileType("Zarr", "*.zarr")]),
        ],
    )


def main() -> None:
    run_file_dialog(build_config())  # outcome handled by the callbacks
    print("recent now:", STORE.recent())


if __name__ == "__main__":
    main()
