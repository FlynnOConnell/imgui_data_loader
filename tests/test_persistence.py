from dataclasses import dataclass
from typing import List, Optional

from imgui_data_loader import JsonPreferenceStore, PickKind, PreferenceStore


@dataclass
class _Result:
    paths: List[str]
    kind: Optional[PickKind] = None


def test_records_and_reads_recent(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    f = tmp_path / "a.tif"
    f.write_text("x")
    store.record_selection(_Result([str(f)]))
    assert store.recent() == [str(f)]
    # last_dir points at the file's parent (which exists)
    assert store.default_dir() == str(tmp_path)


def test_recent_dedup_and_order(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    store.record_selection(_Result(["/a"]))
    store.record_selection(_Result(["/b"]))
    store.record_selection(_Result(["/a"]))  # re-select -> moves to front
    assert store.recent() == ["/a", "/b"]


def test_recent_is_capped(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json", max_recent=3)
    for i in range(10):
        store.record_selection(_Result([f"/f{i}"]))
    assert store.recent() == ["/f9", "/f8", "/f7"]


def test_persists_across_instances(tmp_path):
    p = tmp_path / "recent.json"
    JsonPreferenceStore(path=p).record_selection(_Result(["/x", "/y"]))
    reopened = JsonPreferenceStore(path=p)
    assert reopened.recent() == ["/x", "/y"]


def test_default_dir_empty_when_missing(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    assert store.default_dir() == ""
    store.record_selection(_Result(["/does/not/exist/z.tif"]))
    # parent does not exist -> default_dir falls back to ""
    assert store.default_dir() == ""


def test_empty_selection_is_ignored(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    store.record_selection(_Result([]))
    assert store.recent() == []


def test_default_dir_per_pick_kind(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    files_dir = tmp_path / "files"
    folders_dir = tmp_path / "folders"
    files_dir.mkdir()
    folders_dir.mkdir()
    f = files_dir / "a.tif"
    f.write_text("x")
    store.record_selection(_Result([str(f)], kind=PickKind.OPEN_FILE))
    store.record_selection(_Result([str(folders_dir)], kind=PickKind.SELECT_FOLDER))
    assert store.default_dir(PickKind.OPEN_FILE) == str(files_dir)
    assert store.default_dir(PickKind.SELECT_FOLDER) == str(folders_dir)
    # no kind -> most recent overall
    assert store.default_dir() == str(folders_dir)


def test_default_dir_kind_falls_back_to_global(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    f = tmp_path / "a.tif"
    f.write_text("x")
    store.record_selection(_Result([str(f)], kind=PickKind.OPEN_FILE))
    # never saved a folder pick -> falls back to the global last dir
    assert store.default_dir(PickKind.SELECT_FOLDER) == str(tmp_path)


def test_noarg_default_dir_store_still_works(tmp_path):
    # a legacy store whose default_dir takes no argument must keep working
    from imgui_data_loader.dialog import _store_default_dir

    class _Legacy:
        def default_dir(self):
            return "/legacy"

        def recent(self):
            return []

        def record_selection(self, result):
            pass

    assert _store_default_dir(_Legacy(), PickKind.OPEN_FILE) == "/legacy"
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    assert _store_default_dir(store, None) == ""


def test_json_store_satisfies_protocol(tmp_path):
    store = JsonPreferenceStore(path=tmp_path / "recent.json")
    assert isinstance(store, PreferenceStore)
