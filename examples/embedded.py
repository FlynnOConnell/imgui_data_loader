"""Embed the FileDialog widget inside your own hello_imgui / immapp app.

``close_on_select=False`` keeps the app running when a file is chosen;
``take_result()`` delivers the pick each frame without exiting.

    python examples/embedded.py
"""

from imgui_bundle import hello_imgui, imgui, immapp

from imgui_data_loader import FileDialog, FileDialogConfig, ensure_assets


def main() -> None:
    ensure_assets()  # make the FontAwesome icon font available for the icons

    dlg = FileDialog(
        FileDialogConfig(
            title="Embedded loader",
            close_on_select=False,  # don't exit the app on selection
            show_quit_button=False,
        )
    )
    log = {"last": "nothing yet"}

    def gui() -> None:
        dlg.render()
        result = dlg.take_result()
        if result and result.paths:
            log["last"] = ", ".join(result.paths)
        imgui.separator()
        imgui.text(f"Last selection: {log['last']}")

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Embedded example"
    params.app_window_params.window_geometry.size = (380, 760)
    params.callbacks.show_gui = gui
    immapp.run(runner_params=params)


if __name__ == "__main__":
    main()
