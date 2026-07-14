"""Colors and style for the file dialog.

A :class:`Theme` is a plain dataclass of RGBA float tuples, so it can be
constructed, copied, and inspected without an active imgui context (handy in
tests). Colors are converted to ``imgui.ImVec4`` lazily at draw time.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple

from imgui_bundle import imgui

Color = Tuple[float, float, float, float]


def to_vec4(color) -> "imgui.ImVec4":
    """Coerce an ``(r, g, b[, a])`` tuple (or an ImVec4) to ``imgui.ImVec4``."""
    if isinstance(color, imgui.ImVec4):
        return color
    r, g, b = color[0], color[1], color[2]
    a = color[3] if len(color) > 3 else 1.0
    return imgui.ImVec4(r, g, b, a)


@dataclass(frozen=True)
class Theme:
    """Color palette + a couple of rounding knobs for the dialog.

    Every field is an ``(r, g, b, a)`` float tuple in the 0..1 range. Build a
    variant with :meth:`replace`, e.g. ``Theme.dark().replace(accent=(...))``.
    """

    bg: Color = (0.11, 0.11, 0.12, 1.0)
    bg_card: Color = (0.16, 0.16, 0.17, 1.0)
    accent: Color = (0.20, 0.50, 0.85, 1.0)
    accent_hover: Color = (0.25, 0.55, 0.90, 1.0)
    accent_active: Color = (0.15, 0.45, 0.80, 1.0)
    text: Color = (1.0, 1.0, 1.0, 1.0)
    text_dim: Color = (0.75, 0.75, 0.77, 1.0)
    border: Color = (0.35, 0.35, 0.37, 0.7)
    secondary: Color = (0.35, 0.35, 0.37, 1.0)
    secondary_hover: Color = (0.42, 0.42, 0.44, 1.0)
    secondary_active: Color = (0.28, 0.28, 0.30, 1.0)
    ok: Color = (0.40, 1.00, 0.40, 1.0)
    warn: Color = (1.00, 0.80, 0.20, 1.0)
    err: Color = (1.00, 0.40, 0.40, 1.0)
    na: Color = (0.50, 0.50, 0.50, 1.0)
    frame_bg: Color = (0.22, 0.22, 0.23, 1.0)
    frame_bg_hovered: Color = (0.28, 0.28, 0.29, 1.0)
    separator: Color = (0.35, 0.35, 0.37, 0.6)
    # icon_button face (neutral bg behind the accent-colored icon + label)
    button_face: Color = (0.18, 0.18, 0.20, 1.0)
    button_face_hover: Color = (0.22, 0.22, 0.25, 1.0)
    button_face_active: Color = (0.15, 0.15, 0.17, 1.0)
    frame_rounding: float = 6.0
    child_rounding: float = 6.0

    @staticmethod
    def dark() -> "Theme":
        return Theme()

    @staticmethod
    def light() -> "Theme":
        return Theme(
            bg=(0.94, 0.94, 0.95, 1.0),
            bg_card=(0.99, 0.99, 1.00, 1.0),
            accent=(0.10, 0.45, 0.80, 1.0),
            accent_hover=(0.15, 0.50, 0.85, 1.0),
            accent_active=(0.05, 0.40, 0.75, 1.0),
            text=(0.10, 0.10, 0.12, 1.0),
            text_dim=(0.35, 0.35, 0.40, 1.0),
            border=(0.70, 0.70, 0.74, 0.9),
            secondary=(0.80, 0.80, 0.83, 1.0),
            secondary_hover=(0.86, 0.86, 0.89, 1.0),
            secondary_active=(0.72, 0.72, 0.75, 1.0),
            frame_bg=(0.88, 0.88, 0.90, 1.0),
            frame_bg_hovered=(0.82, 0.82, 0.85, 1.0),
            separator=(0.70, 0.70, 0.74, 0.6),
            button_face=(0.90, 0.90, 0.92, 1.0),
            button_face_hover=(0.85, 0.85, 0.88, 1.0),
            button_face_active=(0.80, 0.80, 0.83, 1.0),
        )

    def replace(self, **changes) -> "Theme":
        """Return a copy with the given fields overridden."""
        return replace(self, **changes)
