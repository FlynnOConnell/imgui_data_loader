"""Asset / config-path helpers.

The dialog relies on the FontAwesome 6 font so button icons render. That font
ships inside ``imgui-bundle`` and hello_imgui loads it into the default font
when its asset lookup can resolve ``fonts/Font_Awesome_6_Free-Solid-900.otf``.
:func:`ensure_assets` guarantees that lookup succeeds — without overriding an
assets folder the host app may already have configured — so the library ships
no fonts of its own.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def imgui_bundle_assets_dir() -> Optional[str]:
    """Path to imgui-bundle's bundled ``assets`` folder, or None."""
    try:
        import imgui_bundle

        p = Path(imgui_bundle.__file__).parent / "assets"
        return str(p) if p.is_dir() else None
    except Exception:
        return None


_ICON_FONT = "fonts/Font_Awesome_6_Free-Solid-900.otf"


def ensure_assets(assets_folder: Optional[str] = None) -> None:
    """Make sure hello_imgui can resolve the FontAwesome icon font.

    Pass ``assets_folder`` to use your own folder (it must contain
    ``fonts/Font_Awesome_6_Free-Solid-900.otf`` for the icons to show); it is
    then set as *the* assets folder. With no argument this never clobbers a
    host app's configured assets folder: if the icon font already resolves,
    nothing is touched, and otherwise imgui-bundle's bundled assets are added
    as an extra search path.
    """
    from imgui_bundle import hello_imgui

    if assets_folder:
        hello_imgui.set_assets_folder(str(assets_folder))
        return
    try:
        if hello_imgui.asset_exists(_ICON_FONT):
            return
    except Exception:
        pass
    folder = imgui_bundle_assets_dir()
    if folder:
        hello_imgui.add_assets_search_path(folder)


def config_dir() -> Path:
    """Per-user config dir (``$XDG_CONFIG_HOME/imgui_data_loader``)."""
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    d = Path(base) / "imgui_data_loader"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_ini_path(name: str = "file_dialog") -> str:
    """Path for hello_imgui's ``.ini`` (window layout) file."""
    return str(config_dir() / f"{name}.ini")
