"""dialog_full_example - a loader that wires up every feature.

A microscopy launcher with a source selector, a two-column action grid (open on
the left, export tiles on the right), a formats panel with recent files, a load
-options popup, persistence, and result callbacks. The custom buttons open the
native picker through `dlg.pick(...)`, so their selections come back on
`on_select` just like the built-in buttons.

    python examples/dialog_full_example.py
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
    center_text,
    icon_button,
    pop_button_style,
    push_button_style,
    run_file_dialog,
)

WINDOW_SIZE = (360, 560)

STORE = JsonPreferenceStore()  # ~/.config/imgui_data_loader/recent.json
STATE = {"source": 0, "recurse": True, "downsample": 1}

SOURCES = ["This computer", "Lab server", "Imaging archive"]
IMAGES = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]

OPEN_IMAGES = ButtonSpec("Open images", PickKind.OPEN_FILE, multiselect=True, filetypes=IMAGES)
OPEN_FOLDER = ButtonSpec("Open folder", PickKind.SELECT_FOLDER)
EXPORT_TIFF = ButtonSpec("Export TIFF", PickKind.SAVE_FILE, filetypes=[FileType("TIFF", "*.tif")])
EXPORT_ZARR = ButtonSpec("Export Zarr", PickKind.SAVE_FILE, filetypes=[FileType("Zarr", "*.zarr")])

FORMATS = [
    ("TIFF", "8/16-bit image stacks"),
    ("Zarr", "chunked N-D arrays"),
    ("HDF5", "hierarchical datasets"),
    ("PNG · JPEG", "single 2-D frames"),
]


def actions(dlg) -> None:
    theme = dlg.theme
    style = imgui.get_style()
    avail = imgui.get_content_region_avail().x
    block = min(avail - hello_imgui.em_size(2), hello_imgui.em_size(16))
    inset = (avail - block) * 0.5  # centers the selector and grid as one block
    gap = style.item_spacing.x

    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + inset)
    imgui.set_next_item_width(block)
    _, STATE["source"] = imgui.combo("##source", STATE["source"], SOURCES)
    imgui.dummy(hello_imgui.em_to_vec2(0, 0.4))

    tile = hello_imgui.em_size(3.4)      # right column: two square export tiles
    open_w = block - tile - gap          # left column takes the remaining width
    origin = imgui.get_cursor_pos()
    x_open, x_export = origin.x + inset, origin.x + inset + open_w + gap
    y_row = origin.y + hello_imgui.em_size(1.1)  # leaves room for the captions

    imgui.set_cursor_pos(imgui.ImVec2(x_open, origin.y))
    imgui.text_colored(imgui.ImVec4(*theme.text_dim), "Open")
    imgui.set_cursor_pos(imgui.ImVec2(x_export, origin.y))
    imgui.text_colored(imgui.ImVec4(*theme.text_dim), "Export")

    imgui.set_cursor_pos(imgui.ImVec2(x_open, y_row))
    if icon_button(fa.ICON_FA_FILE_IMAGE, "Images", imgui.ImVec2(open_w, tile), theme=theme):
        dlg.pick(OPEN_IMAGES)
    imgui.set_cursor_pos(imgui.ImVec2(x_open, y_row + tile + gap))
    if icon_button(fa.ICON_FA_FOLDER_OPEN, "Folder", imgui.ImVec2(open_w, tile), theme=theme):
        dlg.pick(OPEN_FOLDER)

    push_button_style(theme, primary=True)  # filled tiles, icon stacked over label
    imgui.set_cursor_pos(imgui.ImVec2(x_export, y_row))
    hit_tiff = imgui.button(f"{fa.ICON_FA_FLOPPY_DISK}\nTIFF", imgui.ImVec2(tile, tile))
    imgui.set_cursor_pos(imgui.ImVec2(x_export, y_row + tile + gap))
    hit_zarr = imgui.button(f"{fa.ICON_FA_FLOPPY_DISK}\nZarr", imgui.ImVec2(tile, tile))
    pop_button_style()
    if hit_tiff:
        dlg.pick(EXPORT_TIFF)
    if hit_zarr:
        dlg.pick(EXPORT_ZARR)

    imgui.set_cursor_pos(imgui.ImVec2(origin.x, y_row + 2 * tile + gap))


def formats(dlg) -> None:
    theme = dlg.theme
    center_text("Supported formats", theme.accent)
    imgui.dummy(hello_imgui.em_to_vec2(0, 0.15))
    if imgui.begin_table("##formats", 2, imgui.TableFlags_.sizing_fixed_fit):
        imgui.table_setup_column("", imgui.TableColumnFlags_.width_fixed, hello_imgui.em_size(5))
        for name, note in FORMATS:
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text_colored(imgui.ImVec4(*theme.accent), name)
            imgui.table_next_column()
            imgui.text_colored(imgui.ImVec4(*theme.text_dim), note)
        imgui.end_table()

    recent = STORE.recent()
    if recent:
        imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))
        imgui.text_colored(imgui.ImVec4(*theme.text_dim), "Recent")
        for path in recent[:3]:
            imgui.bullet_text(path)


def load_options(dlg) -> None:
    _, STATE["recurse"] = imgui.checkbox("Recurse into subfolders", STATE["recurse"])
    imgui.set_next_item_width(hello_imgui.em_size(9))
    _, STATE["downsample"] = imgui.slider_int("Downsample", STATE["downsample"], 1, 8)


def on_select(result: DialogResult) -> None:
    print(f"source={SOURCES[STATE['source']]} recurse={STATE['recurse']} "
          f"downsample={STATE['downsample']}")
    print("selected:", result.paths)


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Microscopy Loader",
        subtitle="open a dataset to begin",
        theme=Theme.dark().replace(accent=(0.20, 0.75, 0.70, 1.0)),
        buttons=[],  # the two-column grid in `actions` replaces the default column
        persistence=STORE,
        top_draw=actions,
        info=formats,
        options_draw=load_options,
        options_label="Load options",
        quit_label="Close",
        on_select=on_select,
        on_cancel=lambda: print("cancelled"),
    )


def main() -> None:
    run_file_dialog(build_config())
    print("recent now:", STORE.recent())


if __name__ == "__main__":
    main()
