"""03 - Theme + info card.

New vs 02: a custom Theme (start from dark()/light() and .replace() colors) and
an `info` card. `info` is a *list* of callbacks here - each is drawn as its own
section - and the sections use the library's themed helpers (center_text,
text_wrapped_colored, icon_button).

    python examples/03_theme_info.py
"""

import webbrowser

from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui

from imgui_data_loader import (
    FileDialogConfig,
    FileType,
    Theme,
    center_text,
    icon_button,
    run_file_dialog,
    text_wrapped_colored,
)

WINDOW_SIZE = (360, 620)


def formats_section(dlg) -> None:
    center_text("Supported formats", dlg.theme.accent)
    for name, ext in [("TIFF", ".tif / .tiff"), ("Zarr", ".zarr"), ("HDF5", ".h5")]:
        imgui.bullet_text(f"{name}    {ext}")


def help_section(dlg) -> None:
    text_wrapped_colored(
        dlg.theme.text_dim,
        "Folders load every supported file inside, sorted by name.",
    )
    if icon_button(
        fa.ICON_FA_BOOK, "Documentation", imgui.ImVec2(0, 0),
        theme=dlg.theme, tooltip="Open the docs in a browser",
    ):
        webbrowser.open("https://example.com/docs")


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Themed Loader",
        subtitle="teal on charcoal",
        theme=Theme.dark().replace(
            accent=(0.20, 0.75, 0.70, 1.0),
            accent_hover=(0.26, 0.82, 0.77, 1.0),
            accent_active=(0.15, 0.66, 0.62, 1.0),
        ),
        filetypes=[FileType("Images", "*.tif *.tiff *.h5 *.zarr")],
        info=[formats_section, help_section],  # two sections in the card
    )


def main() -> None:
    result = run_file_dialog(build_config())
    print("selected:", result.paths if result else "cancelled")


if __name__ == "__main__":
    main()
