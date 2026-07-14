"""06 - Embedded in your own app (the capstone).

New vs 05: don't use run_file_dialog at all. Render the FileDialog *widget*
inside your own hello_imgui / immapp loop as one panel of a bigger UI. Shows:
  * close_on_select=False + take_result() polling (picking a file doesn't exit),
  * header_draw - a fully custom header,
  * footer_draw - a custom footer built from the library's button helpers,
  * ensure_assets() so the icon font is available in your own runner.

    python examples/06_embedded_app.py
"""

from imgui_bundle import hello_imgui, imgui, immapp

from imgui_data_loader import (
    FileDialog,
    FileDialogConfig,
    center_next_item,
    center_text,
    ensure_assets,
    pop_button_style,
    push_button_style,
)

WINDOW_SIZE = (420, 560)

LOG: list = []


def header(dlg) -> None:
    imgui.dummy(imgui.ImVec2(0, 6))
    center_text("ACME DATA STUDIO", dlg.theme.accent)
    center_text("open a file to begin", dlg.theme.text_dim)


def footer(dlg) -> None:
    imgui.dummy(imgui.ImVec2(0, 6))
    w = 150.0
    center_next_item(w)
    push_button_style(dlg.theme, primary=False)
    if imgui.button("Clear log", imgui.ImVec2(w, 0)):
        LOG.clear()
    pop_button_style()


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        close_on_select=False,   # keep the app alive after a pick
        show_quit_button=False,  # the host app owns quitting
        header_draw=header,
        footer_draw=footer,
    )


def draw(dlg: FileDialog) -> None:
    # the dialog is one panel; render it, then the rest of the app below it
    dlg.render()
    result = dlg.take_result()
    if result and result.paths:
        LOG.extend(result.paths)
    imgui.separator()
    imgui.text_colored(
        dlg.theme.accent if LOG else dlg.theme.text_dim,
        f"loaded {len(LOG)} file(s):",
    )
    for p in LOG[-8:]:
        imgui.bullet_text(p)


def main() -> None:
    ensure_assets()  # make the icon font available inside our own runner
    dlg = FileDialog(build_config())

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Embedded example"
    params.app_window_params.window_geometry.size = (420, 760)
    params.app_window_params.resizable = True
    params.callbacks.show_gui = lambda: draw(dlg)
    immapp.run(runner_params=params)


if __name__ == "__main__":
    main()
