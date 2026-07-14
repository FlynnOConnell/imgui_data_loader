"""Optional persistence for recent files + last-used directory.

Pass any object implementing :class:`PreferenceStore` as
``FileDialogConfig.persistence``. The dialog will seed the picker's start
directory from :meth:`default_dir` and call :meth:`record_selection` after a
successful pick. :class:`JsonPreferenceStore` is a batteries-included default.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from ._assets import config_dir

try:  # Protocol is 3.8+, runtime_checkable too
    from typing import Protocol, runtime_checkable
except ImportError:  # pragma: no cover
    Protocol = object  # type: ignore

    def runtime_checkable(x):  # type: ignore
        return x


@runtime_checkable
class PreferenceStore(Protocol):
    """Minimal interface the dialog uses for persistence."""

    def default_dir(self) -> str:
        """Directory to open the native picker in (``""`` to fall back)."""
        ...

    def recent(self) -> List[str]:
        """Most-recent-first list of previously selected paths."""
        ...

    def record_selection(self, result) -> None:
        """Persist a completed :class:`DialogResult`."""
        ...


class JsonPreferenceStore:
    """A JSON-file-backed :class:`PreferenceStore`.

    Stores a capped most-recent-first list plus the last-used directory.
    """

    def __init__(self, path: Optional[str] = None, max_recent: int = 20):
        self.path = Path(path) if path else (config_dir() / "recent.json")
        self.max_recent = max_recent
        self._data = {"recent": [], "last_dir": ""}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.is_file():
                loaded = json.loads(self.path.read_text())
                if isinstance(loaded, dict):
                    self._data.update(loaded)
        except Exception:
            pass

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._data, indent=2))
        except Exception:
            pass

    def default_dir(self) -> str:
        d = self._data.get("last_dir", "")
        return d if d and Path(d).exists() else ""

    def recent(self) -> List[str]:
        return list(self._data.get("recent", []))

    def record_selection(self, result) -> None:
        paths = list(getattr(result, "paths", None) or [])
        if not paths:
            return
        recent = [p for p in self._data.get("recent", []) if p not in paths]
        for p in reversed(paths):
            recent.insert(0, p)
        self._data["recent"] = recent[: self.max_recent]
        first = Path(paths[0])
        self._data["last_dir"] = str(first if first.is_dir() else first.parent)
        self._save()
