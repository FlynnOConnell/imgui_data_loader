"""Asset / per-user path helpers.

Everything this library writes or looks for on disk lives under one dot
directory, ``~/.imgui_data_loader`` (override with the
``IMGUI_DATA_LOADER_HOME`` env var):

- ``file_dialog.ini`` — hello_imgui's window-layout file (``run_file_dialog``
  pins it here unless ``config.ini_path`` says otherwise)
- ``recent.json`` — :class:`~imgui_data_loader.JsonPreferenceStore`'s default
  location for recent files + last-used directories
- ``assets/`` — optional user assets folder, searched for the icon font

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


def data_dir() -> Path:
    """The per-user dir for everything this library writes.

    ``~/.imgui_data_loader`` by default; override with the
    ``IMGUI_DATA_LOADER_HOME`` env var. Created on first use.
    """
    base = os.environ.get("IMGUI_DATA_LOADER_HOME")
    d = Path(base) if base else (Path.home() / ".imgui_data_loader")
    d.mkdir(parents=True, exist_ok=True)
    return d


def user_assets_dir() -> Path:
    """``~/.imgui_data_loader/assets`` — optional user assets folder.

    Not created automatically; make it yourself to supply the icon font (or
    other assets) without touching the host app's assets folder.
    """
    return data_dir() / "assets"


def ensure_assets(assets_folder: Optional[str] = None) -> None:
    """Make sure hello_imgui can resolve the FontAwesome icon font.

    Pass ``assets_folder`` to use your own folder (it must contain
    ``fonts/Font_Awesome_6_Free-Solid-900.otf`` for the icons to show); it is
    then set as *the* assets folder. With no argument this never clobbers a
    host app's configured assets folder: if the icon font already resolves,
    nothing is touched. Otherwise ``~/.imgui_data_loader/assets`` (if it
    exists) and imgui-bundle's bundled assets are added as extra search
    paths, in that order.
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
    user = user_assets_dir()
    if user.is_dir():
        hello_imgui.add_assets_search_path(str(user))
        try:
            if hello_imgui.asset_exists(_ICON_FONT):
                return
        except Exception:
            pass
    folder = imgui_bundle_assets_dir()
    if folder:
        hello_imgui.add_assets_search_path(folder)


def default_ini_path(name: str = "file_dialog") -> str:
    """Path for hello_imgui's ``.ini`` (window layout) file."""
    return str(data_dir() / f"{name}.ini")
