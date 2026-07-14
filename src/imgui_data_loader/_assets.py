"""Asset / config-path helpers.

The dialog relies on the FontAwesome 6 font so button icons render. That font
ships inside ``imgui-bundle`` and hello_imgui loads it into the default font
when the assets folder points at a directory containing
``fonts/Font_Awesome_6_Free-Solid-900.otf``. :func:`ensure_assets` points
hello_imgui at imgui-bundle's own bundled assets, so the library ships no fonts
of its own.
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


def ensure_assets(assets_folder: Optional[str] = None) -> None:
    """Point hello_imgui at an assets folder that provides the icon font.

    Defaults to imgui-bundle's bundled assets. Pass ``assets_folder`` to use
    your own (it must contain ``fonts/Font_Awesome_6_Free-Solid-900.otf`` for
    the icons to show).
    """
    from imgui_bundle import hello_imgui

    folder = assets_folder or imgui_bundle_assets_dir()
    if folder:
        hello_imgui.set_assets_folder(str(folder))


def config_dir() -> Path:
    """Per-user config dir (``$XDG_CONFIG_HOME/imgui_data_loader``)."""
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    d = Path(base) / "imgui_data_loader"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_ini_path(name: str = "file_dialog") -> str:
    """Path for hello_imgui's ``.ini`` (window layout) file."""
    return str(config_dir() / f"{name}.ini")
