"""02 - Buttons + file types.

New vs 01: branding (title/subtitle), a hand-built `buttons` list covering every
PickKind - open one file, open many, select a folder, save-as - each with its
own icon, tooltip, and filters; a dialog-wide `filetypes` default; a
`default_dir` to start the picker in; and reading `result.kind` to see which
button produced the selection.

    python examples/02_buttons_filetypes.py
"""

from pathlib import Path

from imgui_bundle import icons_fontawesome_6 as fa

from imgui_data_loader import (
    ButtonSpec,
    FileDialogConfig,
    FileType,
    PickKind,
    run_file_dialog,
)


def build_config() -> FileDialogConfig:
    images = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]
    return FileDialogConfig(
        title="Importer",
        subtitle="open anything",
        default_dir=str(Path.home()),
        filetypes=[FileType("Recordings", "*.dat *.bin *.nwb"), FileType("All Files", "*")],
        buttons=[
            ButtonSpec(
                "Open one image",
                PickKind.OPEN_FILE,
                icon=fa.ICON_FA_FILE_IMAGE,
                filetypes=images,          # overrides the dialog-wide filetypes
                tooltip="Pick a single TIFF",
            ),
            ButtonSpec(
                "Open many images",
                PickKind.OPEN_FILE,
                multiselect=True,
                icon=fa.ICON_FA_CLONE,
                filetypes=images,
                tooltip="Pick several TIFFs at once",
            ),
            ButtonSpec(
                "Open a folder",
                PickKind.SELECT_FOLDER,
                icon=fa.ICON_FA_FOLDER_OPEN,
                title="Choose a data folder",
            ),
            ButtonSpec(
                "Export as...",
                PickKind.SAVE_FILE,
                icon=fa.ICON_FA_FLOPPY_DISK,
                filetypes=[FileType("Zarr", "*.zarr")],
                title="Save output",
            ),
        ],
    )


def main() -> None:
    result = run_file_dialog(build_config())
    if not result:
        print("cancelled")
        return
    # result.kind is the PickKind of the button that produced the selection
    if result.kind is PickKind.SAVE_FILE:
        print("save to:", result.path)
    elif result.kind is PickKind.SELECT_FOLDER:
        print("folder :", result.path)
    else:
        print("open   :", result.paths)


if __name__ == "__main__":
    main()
