"""03 - Placement: use imgui to control where things go.

The built-in Options popup is centered over the dialog for you (the library calls
imgui.set_next_window_pos so it never drifts down a tall window). This example
shows the same tools for *your own* content:

  * imgui.set_next_window_pos(pos, cond, pivot) - anchor a popup where you want
    it (here: above the button that opens it) instead of at the mouse cursor.
  * the cursor API (set_cursor_pos_x + get_content_region_avail) - right-align a
    button within the row.

Replaces the footer via `footer_draw`. (Esc still quits - the library handles it
around a custom footer.)

    python examples/03_placement.py
"""

from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui

from imgui_data_loader import (
    FileDialogConfig,
    pop_button_style,
    push_button_style,
    run_file_dialog,
)

WINDOW_SIZE = (360, 420)

_frames = {"n": 0}  # for the auto-open below (screenshot only)


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

    # auto-open once so the captured screenshot shows the placed popup (demo only;
    # in a real app you'd just open it on `clicked`)
    _frames["n"] += 1
    if clicked or _frames["n"] == 3:
        imgui.open_popup("##help")

    # anchor the popup's bottom-right corner to the button's top-right: it opens
    # up and to the left of the button, staying on-screen instead of drifting to
    # the mouse position
    if imgui.is_popup_open("##help"):
        anchor = imgui.ImVec2(btn_max.x, btn_min.y - 6)
        imgui.set_next_window_pos(anchor, imgui.Cond_.appearing, imgui.ImVec2(1.0, 1.0))
    if imgui.begin_popup("##help"):
        imgui.text_colored(dlg.theme.accent, "Anchored to the button")
        imgui.text("via set_next_window_pos")
        imgui.end_popup()


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Placement",
        subtitle="anchored popup + right-aligned button",
        footer_draw=footer,
    )


def main() -> None:
    result = run_file_dialog(build_config())
    print("selected:", result.paths if result else "cancelled")


if __name__ == "__main__":
    main()
