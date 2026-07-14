"""A fully customized dialog: custom buttons, info card, options popup, theme.

    python examples/custom_dialog.py
"""

from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui

from imgui_data_loader import (
    ButtonSpec,
    FileDialogConfig,
    FileType,
    PickKind,
    Theme,
    run_file_dialog,
    text_wrapped_colored,
)

# Options popup writes here; read it back after the dialog closes.
STATE = {"recursive": True, "downsample": 1}


def info(dlg) -> None:
    imgui.text_colored(dlg.theme.accent, "Supported formats")
    for name, ext in [("TIFF", ".tif/.tiff"), ("Zarr", ".zarr"), ("HDF5", ".h5")]:
        imgui.bullet_text(f"{name}  ({ext})")
    text_wrapped_colored(
        dlg.theme.text_dim,
        "Pick a file or a folder. Folders load every supported file inside.",
    )


def options(dlg) -> None:
    _, STATE["recursive"] = imgui.checkbox("Recurse into subfolders", STATE["recursive"])
    imgui.set_next_item_width(120)
    _, STATE["downsample"] = imgui.slider_int("Downsample", STATE["downsample"], 1, 8)


def main() -> None:
    cfg = FileDialogConfig(
        title="Data Importer",
        subtitle="custom example",
        theme=Theme.dark().replace(accent=(0.35, 0.75, 0.55, 1.0)),
        buttons=[
            ButtonSpec(
                "Open image(s)",
                PickKind.OPEN_FILE,
                icon=fa.ICON_FA_FILE_IMAGE,
                multiselect=True,
                filetypes=[
                    FileType("Images", "*.tif *.tiff *.png"),
                    FileType("All Files", "*"),
                ],
            ),
            ButtonSpec(
                "Open folder",
                PickKind.SELECT_FOLDER,
                icon=fa.ICON_FA_FOLDER_OPEN,
            ),
        ],
        info=info,
        options_draw=options,
        options_label="Import options",
    )
    result = run_file_dialog(cfg)
    print("kind:", result.kind)
    print("paths:", result.paths)
    print("options:", STATE)


if __name__ == "__main__":
    main()
