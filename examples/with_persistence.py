"""Remember recent files across runs with JsonPreferenceStore.

The store seeds the picker's start directory from the last used one and shows
previously opened paths in the info card.

    python examples/with_persistence.py
"""

from imgui_bundle import imgui

from imgui_data_loader import (
    FileDialogConfig,
    JsonPreferenceStore,
    run_file_dialog,
)


def main() -> None:
    store = JsonPreferenceStore()  # ~/.config/imgui_data_loader/recent.json

    def recents(dlg) -> None:
        rec = store.recent()
        if not rec:
            imgui.text_colored(dlg.theme.text_dim, "No recent files yet.")
            return
        imgui.text_colored(dlg.theme.accent, "Recent")
        for p in rec[:5]:
            imgui.bullet_text(p)

    result = run_file_dialog(
        FileDialogConfig(
            title="Recent Files Demo",
            persistence=store,
            info=recents,
        )
    )
    print("Selected:", result.paths)
    print("Recent now:", store.recent())


if __name__ == "__main__":
    main()
