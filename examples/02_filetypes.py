"""02 - Branding + file types.

New vs 01: a title/subtitle, a list of FileType filters applied to the file
picker, a default_dir to start in, and reading result.kind to see which button
was used.

    python examples/02_filetypes.py
"""

from pathlib import Path

from imgui_data_loader import FileDialogConfig, FileType, run_file_dialog


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Spike Sorter",
        subtitle="Open a recording",
        filetypes=[
            FileType("Recordings", "*.dat *.bin *.nwb"),
            FileType("NumPy", "*.npy *.npz"),
            FileType("All Files", "*"),
        ],
        default_dir=str(Path.home()),
    )


def main() -> None:
    result = run_file_dialog(build_config())
    if not result:
        print("cancelled")
        return
    # result.kind is the PickKind of the button that produced the selection
    print(f"{result.kind.value}: {result.paths}")


if __name__ == "__main__":
    main()
