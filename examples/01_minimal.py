"""01 - Minimal: one call, default buttons.

The floor of the ladder. `run_file_dialog()` with no configuration gives an
"Open File(s)" + "Select Folder" launcher and returns a DialogResult.

    python examples/01_minimal.py
"""

from imgui_data_loader import FileDialogConfig, run_file_dialog


def build_config() -> FileDialogConfig:
    return FileDialogConfig()  # every option defaulted


def main() -> None:
    result = run_file_dialog(build_config())
    if result:  # truthy only for a real selection
        print("first path :", result.path)
        print("all paths  :", result.paths)
    else:
        print("cancelled")


if __name__ == "__main__":
    main()
