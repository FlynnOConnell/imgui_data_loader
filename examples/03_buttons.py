"""03 - Custom buttons: every PickKind in one dialog.

New vs 02: a hand-built `buttons` list covering all four pick kinds - open a
single file, open many files, select a folder, and save-as - each with its own
icon, tooltip, native-dialog title, and (for file/save) its own filters.

    python examples/03_buttons.py
"""

from imgui_bundle import icons_fontawesome_6 as fa

from imgui_data_loader import (
    ButtonSpec,
    FileDialogConfig,
    FileType,
    PickKind,
    run_file_dialog,
)


def build_config() -> FileDialogConfig:
    tiff = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]
    return FileDialogConfig(
        title="Importer",
        subtitle="pick anything",
        buttons=[
            ButtonSpec(
                "Open one image",
                PickKind.OPEN_FILE,
                icon=fa.ICON_FA_FILE_IMAGE,
                filetypes=tiff,
                tooltip="Pick a single TIFF",
            ),
            ButtonSpec(
                "Open many images",
                PickKind.OPEN_FILE,
                multiselect=True,
                icon=fa.ICON_FA_CLONE,
                filetypes=tiff,
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
    if result.kind is PickKind.SAVE_FILE:
        print("save to:", result.path)
    elif result.kind is PickKind.SELECT_FOLDER:
        print("folder :", result.path)
    else:
        print("open   :", result.paths)


if __name__ == "__main__":
    main()
