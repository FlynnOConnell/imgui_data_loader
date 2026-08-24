"""Reusable, themed imgui helpers.

These are standalone: call them from your own ``info``/``options`` callbacks to
match the dialog's look (centered text, wrapped tooltips, accent icon buttons).
Colors accept either an ``imgui.ImVec4`` or a plain ``(r, g, b[, a])`` tuple.
"""

from __future__ import annotations

import inspect

from imgui_bundle import hello_imgui, imgui

from .theme import Theme, to_vec4


def call_draw(cb, dialog) -> None:
    """Invoke a draw callback, passing ``dialog`` only if it takes an argument.

    Supports ``fn(dialog)``, ``fn()``, bound methods, and ``fn(*args)``.
    """
    if cb is None:
        return
    try:
        params = inspect.signature(cb).parameters.values()
        wants_arg = any(
            p.kind
            in (
                p.POSITIONAL_ONLY,
                p.POSITIONAL_OR_KEYWORD,
                p.VAR_POSITIONAL,
            )
            for p in params
        )
    except (TypeError, ValueError):
        wants_arg = True
    if wants_arg:
        cb(dialog)
    else:
        cb()


def wrapped_tooltip(text: str, wrap_em: float = 24.0) -> None:
    """A tooltip whose text wraps to ``wrap_em`` em units (fits narrow dialogs)."""
    imgui.begin_tooltip()
    try:
        imgui.push_text_wrap_pos(hello_imgui.em_size(wrap_em))
        imgui.text_unformatted(text)
        imgui.pop_text_wrap_pos()
    finally:
        imgui.end_tooltip()


def text_wrapped_colored(color, text: str) -> None:
    """Colored equivalent of ``imgui.text_wrapped``."""
    imgui.push_style_color(imgui.Col_.text, to_vec4(color))
    try:
        imgui.text_wrapped(text)
    finally:
        imgui.pop_style_color()


def center_text(text: str, color=None) -> None:
    """Draw horizontally centered text."""
    avail_w = imgui.get_content_region_avail().x
    text_sz = imgui.calc_text_size(text)
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_w - text_sz.x) * 0.5)
    if color is not None:
        imgui.text_colored(to_vec4(color), text)
    else:
        imgui.text(text)


def center_next_item(width: float) -> None:
    """Move the cursor so the next ``width``-wide item is centered."""
    avail_w = imgui.get_content_region_avail().x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_w - width) * 0.5)


def push_button_style(theme: Theme, primary: bool = True) -> None:
    """Push button colors (accent if ``primary`` else neutral). Pair with
    :func:`pop_button_style`."""
    if primary:
        imgui.push_style_color(imgui.Col_.button, to_vec4(theme.accent))
        imgui.push_style_color(imgui.Col_.button_hovered, to_vec4(theme.accent_hover))
        imgui.push_style_color(imgui.Col_.button_active, to_vec4(theme.accent_active))
    else:
        imgui.push_style_color(imgui.Col_.button, to_vec4(theme.secondary))
        imgui.push_style_color(imgui.Col_.button_hovered, to_vec4(theme.secondary_hover))
        imgui.push_style_color(imgui.Col_.button_active, to_vec4(theme.secondary_active))
    imgui.push_style_color(imgui.Col_.text, to_vec4(theme.text))
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, theme.frame_rounding)
    imgui.push_style_var(imgui.StyleVar_.frame_border_size, 0.0)


def pop_button_style() -> None:
    imgui.pop_style_var(2)
    imgui.pop_style_color(4)


def icon_button(
    icon: str,
    label: str,
    size,
    theme: Theme = None,
    tooltip: str = "",
) -> bool:
    """A neutral-faced button with an accent-colored icon + label and a blue
    outline. ``icon`` may be empty. Returns True on click."""
    if theme is None:
        theme = Theme.dark()
    imgui.push_style_color(imgui.Col_.button, to_vec4(theme.button_face))
    imgui.push_style_color(imgui.Col_.button_hovered, to_vec4(theme.button_face_hover))
    imgui.push_style_color(imgui.Col_.button_active, to_vec4(theme.button_face_active))
    imgui.push_style_color(imgui.Col_.text, to_vec4(theme.accent))
    imgui.push_style_color(imgui.Col_.border, to_vec4(theme.accent))
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, theme.frame_rounding)
    imgui.push_style_var(imgui.StyleVar_.frame_border_size, 1.5)

    button_text = f"{icon}  {label}" if icon else label
    clicked = imgui.button(button_text, size)
    if tooltip and imgui.is_item_hovered():
        wrapped_tooltip(tooltip)

    imgui.pop_style_var(2)
    imgui.pop_style_color(5)
    return clicked
