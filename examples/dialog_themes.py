"""dialog_themes - a light theme, a resized window, and hand-placed UI.

A light-themed session browser. Alongside the theme it shows how to control
where your own UI goes, using the same imgui calls the library uses internally:

  * imgui.set_next_window_pos(pos, cond, pivot) - anchor a popup where you want
    it (here: above the button that opens it) instead of at the mouse cursor.
  * the cursor API (set_cursor_pos_x + get_content_region_avail) - right-align a
    button within the row.

The window is sized through `window_size`, and the footer is replaced via
`footer_draw`. (Esc still quits - the library handles it around a custom footer.)

    python examples/dialog_themes.py
"""

from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui

from imgui_data_loader import (
    FileDialogConfig,
    Theme,
    pop_button_style,
    push_button_style,
    run_file_dialog,
)

WINDOW_SIZE = (400, 300)


def footer(dlg) -> None:
    imgui.dummy(imgui.ImVec2(0, 8))

    # right-align a fixed-width button: advance the cursor by (avail - width)
    width = 130.0
    avail = imgui.get_content_region_avail().x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + avail - width)

    push_button_style(dlg.theme, primary=False)
    clicked = imgui.button(f"{fa.ICON_FA_CIRCLE_INFO}  Help", imgui.ImVec2(width, 0))
    pop_button_style()
    btn_min, btn_max = imgui.get_item_rect_min(), imgui.get_item_rect_max()

    if clicked:
        imgui.open_popup("##help")

    # anchor the popup's bottom-right corner to the button's top-right: it opens
    # up and to the left of the button, staying on-screen instead of drifting to
    # the mouse position
    if imgui.is_popup_open("##help"):
        anchor = imgui.ImVec2(btn_max.x, btn_min.y - 6)
        imgui.set_next_window_pos(anchor, imgui.Cond_.appearing, imgui.ImVec2(1.0, 1.0))
    if imgui.begin_popup("##help"):
        imgui.text_colored(dlg.theme.accent, "Where are my sessions?")
        imgui.text("Point at the folder that holds each\nrecording's raw files.")
        imgui.end_popup()


# Module-level so scripts/capture_docs.py can drive the dialog for screenshots
# without running main() (which starts its own blocking event loop).
CONFIG = FileDialogConfig(
    title="Session Browser",
    subtitle="open a recording to inspect it",
    theme=Theme.light(),
    window_size=WINDOW_SIZE,
    footer_draw=footer,
)


def main() -> None:
    result = run_file_dialog(CONFIG)
    print("selected:", result.paths if result else "cancelled")


if __name__ == "__main__":
    main()
