"""One-shot harness: open the dialog in its own window and return the result."""

from __future__ import annotations

import os
from typing import Optional

from ._assets import default_ini_path, ensure_assets
from .config import DialogResult, FileDialogConfig
from .dialog import FileDialog


def run_file_dialog(
    config: Optional[FileDialogConfig] = None,
    *,
    runner_params=None,
) -> DialogResult:
    """Show the dialog, block until the user picks or quits, return the result.

    Parameters
    ----------
    config : FileDialogConfig | None
        Dialog configuration.
    runner_params : hello_imgui.RunnerParams | None
        Advanced: supply your own runner params (e.g. to select a null backend
        for headless tests). Window title/size/ini are filled in from
        ``config`` only when not already set.

    Returns
    -------
    DialogResult
        ``bool(result)`` is True for a real selection; the paths are in
        ``result.paths``. A quit / cancel yields an empty, ``cancelled`` result.
    """
    from imgui_bundle import hello_imgui, immapp

    config = config or FileDialogConfig()
    ensure_assets(config.assets_folder)

    dlg = FileDialog(config)
    params = runner_params if runner_params is not None else hello_imgui.RunnerParams()
    params.app_window_params.window_title = config.window_title or config.title
    if config.window_size:
        params.app_window_params.window_geometry.size = tuple(config.window_size)
        params.app_window_params.window_geometry.size_auto = False
    params.app_window_params.resizable = config.resizable
    # Route the layout .ini. hello_imgui resolves ini_filename relative to
    # ini_folder_type (default: the current working directory), so an empty or
    # relative name would drop a file next to wherever the app was launched.
    # Pin it to an absolute path instead (default: ~/.config/imgui_data_loader).
    if not params.ini_filename:
        ini = config.ini_path or default_ini_path()
        params.ini_filename = ini
        if os.path.isabs(ini):
            params.ini_folder_type = hello_imgui.IniFolderType.absolute_path
            parent = os.path.dirname(ini)
            if parent:
                os.makedirs(parent, exist_ok=True)
    dlg.apply_host_theme(params)
    params.callbacks.show_gui = dlg.render

    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    addons.with_implot = False
    addons.with_implot3d = False

    immapp.run(runner_params=params, add_ons_params=addons)

    return dlg.result or DialogResult(paths=[], kind=None, cancelled=True)
