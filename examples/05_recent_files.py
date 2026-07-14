"""05 - Recent files with the built-in JSON store.

New vs 04: a JsonPreferenceStore records selections and seeds the picker's
start directory from the last one used. The info card lists recent picks.

    python examples/05_recent_files.py
"""

from imgui_bundle import imgui

from imgui_data_loader import FileDialogConfig, JsonPreferenceStore, run_file_dialog

WINDOW_SIZE = (360, 560)

STORE = JsonPreferenceStore()  # ~/.config/imgui_data_loader/recent.json


def recent_panel(dlg) -> None:
    recent = STORE.recent()
    if not recent:
        imgui.text_colored(dlg.theme.text_dim, "No recent files yet.")
        return
    imgui.text_colored(dlg.theme.accent, "Recent")
    for path in recent[:6]:
        imgui.bullet_text(path)


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Recent Files",
        subtitle="remembers across runs",
        persistence=STORE,  # seeds start dir + records selections
        info=recent_panel,
    )


def main() -> None:
    result = run_file_dialog(build_config())
    print("picked    :", result.paths if result else "cancelled")
    print("recent now:", STORE.recent())


if __name__ == "__main__":
    main()
