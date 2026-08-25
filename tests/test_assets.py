import shutil
from pathlib import Path

from imgui_data_loader import ensure_assets
from imgui_data_loader._assets import (
    _ICON_FONT,
    data_dir,
    default_ini_path,
    imgui_bundle_assets_dir,
    user_assets_dir,
)


def test_data_dir_defaults_to_home_dotdir(monkeypatch):
    monkeypatch.delenv("IMGUI_DATA_LOADER_HOME", raising=False)
    assert data_dir() == Path.home() / ".imgui_data_loader"


def test_data_dir_env_override(tmp_path, monkeypatch):
    home = tmp_path / "custom"
    monkeypatch.setenv("IMGUI_DATA_LOADER_HOME", str(home))
    d = data_dir()
    assert d == home
    assert d.is_dir()  # created on first use
    assert user_assets_dir() == home / "assets"
    assert not user_assets_dir().exists()  # never auto-created


def test_default_ini_path_lives_in_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("IMGUI_DATA_LOADER_HOME", str(tmp_path / "home"))
    assert default_ini_path() == str(tmp_path / "home" / "file_dialog.ini")
    assert default_ini_path("other") == str(tmp_path / "home" / "other.ini")


def test_ensure_assets_finds_user_assets_dir(tmp_path, monkeypatch):
    # With the icon font unresolvable and no explicit folder, ensure_assets
    # picks up ~/.imgui_data_loader/assets as a search path.
    from imgui_bundle import hello_imgui

    monkeypatch.setenv("IMGUI_DATA_LOADER_HOME", str(tmp_path / "home"))
    user = user_assets_dir()
    (user / "fonts").mkdir(parents=True)
    src = imgui_bundle_assets_dir()
    assert src is not None
    shutil.copy2(str(Path(src) / _ICON_FONT), str(user / _ICON_FONT))

    empty = tmp_path / "empty_assets"
    empty.mkdir()
    try:
        hello_imgui.clear_assets_search_paths()
        hello_imgui.set_assets_folder(str(empty))
        assert not hello_imgui.asset_exists(_ICON_FONT)

        ensure_assets()
        assert hello_imgui.asset_exists(_ICON_FONT)
    finally:
        # global hello_imgui state: point back at the bundled assets so later
        # tests (headless render) still resolve their fonts
        hello_imgui.clear_assets_search_paths()
        hello_imgui.set_assets_folder(src)
