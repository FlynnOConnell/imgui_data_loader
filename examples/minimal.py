"""Minimal one-shot dialog.

    python examples/minimal.py
"""

from imgui_data_loader import FileDialogConfig, FileType, run_file_dialog


def main() -> None:
    result = run_file_dialog(
        FileDialogConfig(
            title="imgui_data_loader",
            subtitle="Minimal example",
            filetypes=[
                FileType("Images", "*.tif *.tiff *.png *.jpg"),
                FileType("All Files", "*"),
            ],
        )
    )
    if result:
        print("Selected:", result.paths)
    else:
        print("Cancelled")


if __name__ == "__main__":
    main()
