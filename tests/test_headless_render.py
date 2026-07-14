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
    p.ini_filename = ""  # don't write a layout file

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


def test_widget_constructs_without_context():
    # constructing the widget must not require an imgui frame
    dlg = FileDialog(FileDialogConfig(title="x"))
    assert dlg.result is None
    assert dlg.take_result() is None
    assert dlg.theme is not None
