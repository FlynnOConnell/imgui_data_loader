"""imgui_data_loader — a themed, configurable imgui file/folder open dialog.

Quick start
-----------
>>> from imgui_data_loader import run_file_dialog, FileDialogConfig, FileType
>>> result = run_file_dialog(FileDialogConfig(
...     title="My App",
...     filetypes=[FileType("Images", "*.tif *.png"), FileType("All Files", "*")],
... ))
>>> if result:
...     print(result.paths)

Embed it in your own imgui/hello_imgui app instead:
>>> from imgui_data_loader import FileDialog, FileDialogConfig
>>> dlg = FileDialog(FileDialogConfig(close_on_select=False))
>>> # params.callbacks.show_gui = dlg.render
>>> # each frame: r = dlg.take_result(); if r: ...
"""

from __future__ import annotations

from ._assets import ensure_assets
from .config import (
    ButtonSpec,
    DialogResult,
    FileDialogConfig,
    FileType,
    PickKind,
    flatten_filters,
)
from .dialog import FileDialog
from .persistence import JsonPreferenceStore, PreferenceStore
from .runner import run_file_dialog
from .theme import Theme, to_vec4
from .widgets import (
    call_draw,
    center_next_item,
    center_text,
    icon_button,
    pop_button_style,
    push_button_style,
    text_wrapped_colored,
    wrapped_tooltip,
)

__version__ = "0.1.0"

__all__ = [
    # config
    "FileDialogConfig",
    "FileType",
    "ButtonSpec",
    "PickKind",
    "DialogResult",
    "flatten_filters",
    # dialog + harness
    "FileDialog",
    "run_file_dialog",
    "ensure_assets",
    # theme
    "Theme",
    "to_vec4",
    # persistence
    "PreferenceStore",
    "JsonPreferenceStore",
    # reusable widgets
    "icon_button",
    "wrapped_tooltip",
    "text_wrapped_colored",
    "center_text",
    "center_next_item",
    "push_button_style",
    "pop_button_style",
    "call_draw",
    # meta
    "__version__",
]
