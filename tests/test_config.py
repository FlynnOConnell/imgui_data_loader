from imgui_data_loader import (
    ButtonSpec,
    DialogResult,
    FileDialogConfig,
    FileType,
    PickKind,
    flatten_filters,
)


def test_filetype_joins_list_patterns():
    assert FileType("Images", ["*.tif", "*.png"]).patterns == "*.tif *.png"
    assert FileType("All", "*").patterns == "*"


def test_flatten_filters_alternates_name_pattern():
    fts = [FileType("Images", "*.tif *.png"), FileType("All Files", "*")]
    assert flatten_filters(fts) == ["Images", "*.tif *.png", "All Files", "*"]


def test_dialog_result_truthiness_and_path():
    empty = DialogResult()
    assert not empty
    assert empty.path is None

    picked = DialogResult(paths=["/a", "/b"], kind=PickKind.OPEN_FILE)
    assert picked
    assert picked.path == "/a"

    cancelled = DialogResult(paths=["/a"], cancelled=True)
    assert not cancelled  # cancelled overrides non-empty paths


def test_default_config_has_two_buttons():
    cfg = FileDialogConfig()
    assert len(cfg.buttons) == 2
    assert cfg.buttons[0].kind == PickKind.OPEN_FILE
    assert cfg.buttons[0].multiselect is True
    assert cfg.buttons[1].kind == PickKind.SELECT_FOLDER
    # default buttons carry icons
    assert all(b.icon for b in cfg.buttons)


def test_info_callbacks_normalization():
    assert FileDialogConfig(info=None).info_callbacks() == []

    def one(dlg):
        pass

    assert FileDialogConfig(info=one).info_callbacks() == [one]

    def two(dlg):
        pass

    assert FileDialogConfig(info=[one, two]).info_callbacks() == [one, two]


def test_button_filetypes_override():
    b = ButtonSpec("x", PickKind.OPEN_FILE, filetypes=[FileType("Zarr", "*.zarr")])
    assert flatten_filters(b.filetypes) == ["Zarr", "*.zarr"]
