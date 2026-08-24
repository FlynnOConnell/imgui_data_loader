"""dialog_minimal - one call, everything defaulted.

`run_file_dialog()` with no configuration gives an "Open File(s)" + "Select
Folder" launcher and returns a DialogResult.

    python examples/dialog_minimal.py
"""

from imgui_data_loader import FileDialogConfig, run_file_dialog


# Module-level so scripts/capture_docs.py can drive the dialog for screenshots
# without running main() (which starts its own blocking event loop).
CONFIG = FileDialogConfig()  # every option defaulted


def main() -> None:
    result = run_file_dialog(CONFIG)
    if result:  # truthy only for a real selection
        print("first path :", result.path)
        print("all paths  :", result.paths)
    else:
        print("cancelled")


if __name__ == "__main__":
    main()
