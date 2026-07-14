"""dialog_complex - a microscopy loader wired to every feature.

A realistic launcher for an imaging pipeline: pick the dataset type, jot
acquisition notes, then open images or a folder (or export a converted volume).
It carries a custom theme, an info card, a load-options popup, recent-files
history, and result callbacks. Each imgui widget returns `(changed, new_value)`
- keep the value.

The dataset picker and the notes field are sized to the same width the dialog
uses for its buttons, so the whole column lines up.

    python examples/dialog_complex.py
"""

from imgui_bundle import hello_imgui
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
    center_next_item,
    center_text,
    run_file_dialog,
)

WINDOW_SIZE = (360, 680)

STORE = JsonPreferenceStore()  # ~/.config/imgui_data_loader/recent.json
STATE = {
    "dataset": 1,
    "notes": "Sample A2 · 40x · GCaMP6f",
    "recurse": True,
    "downsample": 1,
}
DATASETS = ["2D image", "3D volume", "Time series"]
IMAGES = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]


def _row_width() -> float:
    # the same width the dialog gives its buttons, so the row lines up with them
    return min(
        imgui.get_content_region_avail().x - hello_imgui.em_size(2),
        hello_imgui.em_size(16),
    )


def controls(dlg) -> None:  # top_draw: dataset picker + notes, matched to buttons
    width = _row_width()
    center_next_item(width)
    _, STATE["dataset"] = imgui.combo("##dataset", STATE["dataset"], DATASETS)
    center_next_item(width)
    _, STATE["notes"] = imgui.input_text_multiline(
        "##notes", STATE["notes"], imgui.ImVec2(width, hello_imgui.em_size(3.2))
    )


def info(dlg) -> None:  # info card contents
    center_text("Supported formats", dlg.theme.accent)
    imgui.bullet_text("TIFF / Zarr / HDF5")
    recent = STORE.recent()
    if recent:
        imgui.text_colored(dlg.theme.text_dim, "Recent:")
        for path in recent[:3]:
            imgui.bullet_text(path)


def options(dlg) -> None:  # options_draw: the load-options popup body
    _, STATE["recurse"] = imgui.checkbox("Recurse into subfolders", STATE["recurse"])
    imgui.set_next_item_width(140)
    _, STATE["downsample"] = imgui.slider_int("Downsample", STATE["downsample"], 1, 8)


def on_select(result: DialogResult) -> None:
    print(f"dataset={DATASETS[STATE['dataset']]} recurse={STATE['recurse']} "
          f"downsample={STATE['downsample']}")
    print("notes   :", STATE["notes"])
    print("selected:", result.paths)


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Microscopy Loader",
        subtitle="load an acquisition to begin",
        theme=Theme.dark().replace(accent=(0.20, 0.75, 0.70, 1.0)),
        persistence=STORE,              # seeds start dir + records selections
        top_draw=controls,
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
