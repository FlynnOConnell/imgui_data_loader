"""07 - A custom PreferenceStore.

New vs 06: persistence is just a protocol (default_dir / recent /
record_selection). Implement it yourself to back "recent files" with anything.
This store keeps a per-project history in a project-local JSON file and always
starts the picker in the project directory.

    python examples/07_custom_store.py
"""

import json
from pathlib import Path
from typing import List

from imgui_bundle import imgui

from imgui_data_loader import FileDialogConfig, run_file_dialog


class ProjectStore:
    """Implements the PreferenceStore protocol."""

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.file = self.project_dir / ".loader_history.json"
        self._recent: List[str] = []
        if self.file.exists():
            try:
                self._recent = json.loads(self.file.read_text())
            except Exception:
                self._recent = []

    def default_dir(self) -> str:
        return str(self.project_dir)  # always start in the project

    def recent(self) -> List[str]:
        return list(self._recent)

    def record_selection(self, result) -> None:
        for p in reversed(result.paths):
            if p in self._recent:
                self._recent.remove(p)
            self._recent.insert(0, p)
        self._recent = self._recent[:10]
        try:
            self.file.write_text(json.dumps(self._recent, indent=2))
        except Exception:
            pass


STORE = ProjectStore(Path.cwd())


def recents(dlg) -> None:
    imgui.text_colored(dlg.theme.text_dim, f"project: {STORE.project_dir.name}/")
    recent = STORE.recent()
    if not recent:
        imgui.bullet_text("(no history yet)")
    for p in recent[:6]:
        imgui.bullet_text(Path(p).name)


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Project Loader",
        subtitle="history stays in the project",
        persistence=STORE,
        info=recents,
    )


def main() -> None:
    result = run_file_dialog(build_config())
    print("picked:", result.paths if result else "cancelled")


if __name__ == "__main__":
    main()
