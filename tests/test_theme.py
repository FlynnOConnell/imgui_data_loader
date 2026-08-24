import pytest

from imgui_data_loader import Theme, to_vec4


def test_dark_and_light_differ():
    assert Theme.dark().bg != Theme.light().bg


def test_replace_is_immutable():
    base = Theme.dark()
    variant = base.replace(accent=(1.0, 0.0, 0.0, 1.0))
    assert variant.accent == (1.0, 0.0, 0.0, 1.0)
    assert base.accent != variant.accent  # original untouched
    with pytest.raises(Exception):
        base.accent = (0, 0, 0, 1)  # frozen dataclass


def test_to_vec4_from_tuple():
    v = to_vec4((0.1, 0.2, 0.3))
    assert (round(v.x, 3), round(v.y, 3), round(v.z, 3), v.w) == (0.1, 0.2, 0.3, 1.0)

    v = to_vec4((0.1, 0.2, 0.3, 0.5))
    assert round(v.w, 3) == 0.5


def test_to_vec4_passthrough_imvec4():
    from imgui_bundle import imgui

    src = imgui.ImVec4(0.4, 0.5, 0.6, 0.7)
    assert to_vec4(src) is src
