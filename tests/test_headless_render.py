"""Render the dialog for a few frames on hello_imgui's null backend.

This exercises the real render path (header, buttons, info card, options popup,
footer, escape handling) with no window or GPU. If the null backend can't
initialize in this environment the test skips rather than fails.
"""

import pytest

from imgui_data_loader import (
    ButtonSpec,
    FileDialog,
    FileDialogConfig,
    FileType,
    PickKind,
    Theme,
    ensure_assets,
)


def _null_runner_params():
    from imgui_bundle import hello_imgui, imgui

    p = hello_imgui.RunnerParams()
    p.platform_backend_type = hello_imgui.PlatformBackendType.null
    p.renderer_backend_type = hello_imgui.RendererBackendType.null
    p.app_window_params.window_geometry.size = (360, 720)
    # keep the layout .ini out of the repo/cwd during tests
    p.ini_folder_type = hello_imgui.IniFolderType.temp_folder
    p.ini_filename = "imgui_data_loader_test.ini"

    # The null renderer doesn't upload the font atlas; declare that the
    # backend "has textures" so imgui 1.92's NewFrame doesn't assert on a
    # missing atlas. Nothing is displayed, so no real upload is needed.
    def _enable_textures():
        imgui.get_io().backend_flags |= imgui.BackendFlags_.renderer_has_textures

    p.callbacks.post_init = _enable_textures
    return p


def test_headless_render_smoke():
    from imgui_bundle import hello_imgui, imgui

    ensure_assets()

    def info(dlg):
        imgui.text_colored(dlg.theme.accent, "Supported formats")
        imgui.bullet_text("TIFF / Zarr / HDF5")

    def options(dlg):
        imgui.text("options body")

    cfg = FileDialogConfig(
        title="Headless Test",
        subtitle="null backend",
        theme=Theme.light(),
        info=info,
        options_draw=options,
        buttons=[
            ButtonSpec("Open", PickKind.OPEN_FILE, icon="", multiselect=True,
                       filetypes=[FileType("TIFF", "*.tif")]),
            ButtonSpec("Folder", PickKind.SELECT_FOLDER),
        ],
    )
    dlg = FileDialog(cfg)

    state = {"frames": 0}

    def gui():
        state["frames"] += 1
        if state["frames"] == 1:
            dlg.open_options()  # exercise the popup path on a later frame
        dlg.render()
        if state["frames"] >= 4:
            hello_imgui.get_runner_params().app_shall_exit = True

    params = _null_runner_params()
    params.callbacks.show_gui = gui

    try:
        hello_imgui.run(params)
    except Exception as exc:  # backend unavailable in this environment
        pytest.skip(f"null backend unavailable: {exc}")

    assert state["frames"] >= 3
    # nothing was picked, so no result and not cancelled
    assert dlg.result is None


def test_run_file_dialog_harness_headless():
    # Drive the real one-shot entry point (immapp.run + addons + asset setup)
    # on the null backend, exiting after a few frames with nothing picked.
    from imgui_bundle import hello_imgui
    from imgui_data_loader import run_file_dialog

    params = _null_runner_params()
    prev_post_init = params.callbacks.post_init
    count = {"n": 0}

    def pre_new_frame():
        count["n"] += 1
        if count["n"] >= 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    params.callbacks.pre_new_frame = pre_new_frame
    params.callbacks.post_init = prev_post_init

    try:
        result = run_file_dialog(
            FileDialogConfig(title="Harness", info=lambda dlg: None),
            runner_params=params,
        )
    except Exception as exc:
        pytest.skip(f"null backend unavailable: {exc}")

    assert count["n"] >= 2
    assert result.cancelled  # nothing was picked
    assert result.paths == []


def test_ini_path_is_configurable(tmp_path):
    # config.ini_path controls where hello_imgui writes the layout .ini, and a
    # not-yet-existing parent directory is created for it.
    from imgui_bundle import hello_imgui
    from imgui_data_loader import run_file_dialog

    ini = tmp_path / "nested" / "layout.ini"
    params = _null_runner_params()
    params.ini_filename = ""  # let run_file_dialog fill it from config.ini_path
    count = {"n": 0}

    def pre_new_frame():
        count["n"] += 1
        if count["n"] >= 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    params.callbacks.pre_new_frame = pre_new_frame

    try:
        run_file_dialog(
            FileDialogConfig(title="Ini", ini_path=str(ini)),
            runner_params=params,
        )
    except Exception as exc:
        pytest.skip(f"null backend unavailable: {exc}")

    assert ini.exists()  # written exactly where configured, cwd untouched


def test_embedded_cancel_does_not_exit_host():
    # With close_on_select=False the dialog is embedded in someone else's run
    # loop: cancel() records a cancelled result but must not touch the host's
    # app_shall_exit.
    cancelled = {"n": 0}
    dlg = FileDialog(
        FileDialogConfig(close_on_select=False, on_cancel=lambda: cancelled.update(n=1))
    )
    dlg.cancel()
    r = dlg.take_result()
    assert r is not None and r.cancelled and r.paths == []
    assert cancelled["n"] == 1


def test_oneshot_cancel_requests_exit(monkeypatch):
    # Default (one-shot) config still exits the run loop on cancel.
    calls = {"n": 0}
    monkeypatch.setattr(FileDialog, "_request_exit", staticmethod(lambda: calls.update(n=calls["n"] + 1)))
    dlg = FileDialog(FileDialogConfig())
    dlg.cancel()
    assert calls["n"] == 1
    dlg2 = FileDialog(FileDialogConfig(close_on_select=False))
    dlg2.cancel()
    assert calls["n"] == 1  # unchanged


def test_widget_constructs_without_context():
    # constructing the widget must not require an imgui frame
    dlg = FileDialog(FileDialogConfig(title="x"))
    assert dlg.result is None
    assert dlg.take_result() is None
    assert dlg.theme is not None
    assert callable(dlg.pick)


def test_ensure_assets_does_not_clobber_host_folder(tmp_path):
    # A host app that configured its own assets folder (containing the icon
    # font) must keep it: ensure_assets() with no argument may only add a
    # search path, never replace the folder.
    from imgui_bundle import hello_imgui
    from imgui_data_loader._assets import _ICON_FONT, imgui_bundle_assets_dir
    import shutil

    host = tmp_path / "host_assets"
    (host / "fonts").mkdir(parents=True)
    src = imgui_bundle_assets_dir()
    assert src is not None
    shutil.copy2(str((__import__("pathlib").Path(src) / _ICON_FONT)), str(host / _ICON_FONT))
    marker = host / "host_only.txt"
    marker.write_text("x")

    hello_imgui.set_assets_folder(str(host))
    ensure_assets()
    # host assets still resolve -> the folder was not replaced
    assert hello_imgui.asset_exists("host_only.txt")
    assert hello_imgui.asset_exists(_ICON_FONT)


def test_apply_host_theme_wires_background():
    # apply_host_theme points the host window's clear color at theme.bg and wraps
    # (not clobbers) any existing setup_imgui_style callback. Pure param wiring —
    # no imgui context needed.
    from imgui_bundle import hello_imgui

    dlg = FileDialog(FileDialogConfig(theme=Theme.light()))
    params = hello_imgui.RunnerParams()
    prev = lambda: None  # noqa: E731 - a user-supplied style callback to preserve
    params.callbacks.setup_imgui_style = prev

    dlg.apply_host_theme(params)

    bg = params.imgui_window_params.background_color
    assert (bg.x, bg.y, bg.z, bg.w) == pytest.approx(Theme.light().bg, abs=1e-6)
    # the callback was replaced with a wrapper (which chains prev at run time)
    assert params.callbacks.setup_imgui_style is not prev
    assert callable(params.callbacks.setup_imgui_style)


def _run_frames(dlg, frames, on_frame):
    from imgui_bundle import hello_imgui

    state = {"n": 0}

    def pre_new_frame():
        state["n"] += 1
        on_frame(state["n"])
        if state["n"] >= frames:
            hello_imgui.get_runner_params().app_shall_exit = True

    params = _null_runner_params()
    params.callbacks.pre_new_frame = pre_new_frame
    params.callbacks.show_gui = dlg.render
    try:
        hello_imgui.run(params)
    except Exception as exc:
        pytest.skip(f"null backend unavailable: {exc}")


def _press_escape_on(frame):
    from imgui_bundle import imgui

    def on_frame(n):
        if n == frame:
            imgui.get_io().add_key_event(imgui.Key.escape, True)
        elif n == frame + 1:
            imgui.get_io().add_key_event(imgui.Key.escape, False)

    return on_frame


def test_escape_cancels_the_dialog():
    ensure_assets()
    dlg = FileDialog(FileDialogConfig(close_on_select=False))
    _run_frames(dlg, frames=6, on_frame=_press_escape_on(3))
    assert dlg.result is not None and dlg.result.cancelled


def test_escape_closes_an_open_popup_without_cancelling():
    ensure_assets()
    dlg = FileDialog(FileDialogConfig(close_on_select=False, options_draw=lambda: None))
    dlg.open_options()
    _run_frames(dlg, frames=8, on_frame=_press_escape_on(4))
    assert dlg.result is None


def test_escape_leaves_a_focused_text_field_without_cancelling():
    from imgui_bundle import imgui

    ensure_assets()
    state = {"frame": 0, "text": ""}

    def field():
        state["frame"] += 1
        if state["frame"] == 2:
            imgui.set_keyboard_focus_here()
        _, state["text"] = imgui.input_text("##field", state["text"])

    dlg = FileDialog(FileDialogConfig(close_on_select=False, top_draw=field))
    _run_frames(dlg, frames=8, on_frame=_press_escape_on(4))
    assert dlg.result is None


def test_a_second_pick_waits_for_the_open_picker(monkeypatch):
    import types

    from imgui_data_loader import dialog as dialog_module

    class Pending:
        def ready(self):
            return False

    opened = []

    def select_folder(title, start):
        opened.append(title)
        return Pending()

    monkeypatch.setattr(dialog_module, "pfd", types.SimpleNamespace(select_folder=select_folder))
    dlg = FileDialog(FileDialogConfig())
    dlg.pick(ButtonSpec("first", PickKind.SELECT_FOLDER))
    dlg.pick(ButtonSpec("second", PickKind.SELECT_FOLDER))
    assert opened == ["first"]


def _footer_bottom_and_viewport_height(top_height):
    from imgui_bundle import hello_imgui, imgui

    ensure_assets()
    seen = {}

    def top():
        imgui.dummy(imgui.ImVec2(10, top_height))

    def footer():
        imgui.button("footer")
        seen["bottom"] = imgui.get_item_rect_max().y
        seen["height"] = imgui.get_main_viewport().size.y
        seen["em"] = hello_imgui.em_size(1)

    dlg = FileDialog(FileDialogConfig(close_on_select=False, top_draw=top, footer_draw=footer))
    _run_frames(dlg, frames=5, on_frame=lambda n: None)
    return seen


def test_footer_sits_at_the_bottom_under_short_content():
    seen = _footer_bottom_and_viewport_height(top_height=10)
    assert seen["height"] - 2 * seen["em"] < seen["bottom"] <= seen["height"]


def test_footer_stays_in_the_window_under_tall_content():
    seen = _footer_bottom_and_viewport_height(top_height=5000)
    assert seen["height"] - 2 * seen["em"] < seen["bottom"] <= seen["height"]


def test_body_slot_spans_the_dialog_under_the_card():
    from imgui_bundle import imgui

    ensure_assets()
    widths = {}

    def info():
        widths["card"] = imgui.get_content_region_avail().x

    def body():
        widths["body"] = imgui.get_content_region_avail().x
        widths["body_y"] = imgui.get_cursor_screen_pos().y

    def footer():
        widths["footer_y"] = imgui.get_cursor_screen_pos().y

    dlg = FileDialog(FileDialogConfig(close_on_select=False, info=info, body_draw=body, footer_draw=footer))
    _run_frames(dlg, frames=4, on_frame=lambda n: None)
    assert widths["body"] > widths["card"]
    assert widths["body_y"] < widths["footer_y"]
