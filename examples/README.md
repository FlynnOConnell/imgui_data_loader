# Examples

A ladder from the one-liner to a full embedded app. Each step uses options the
previous one didn't. They open a real window, so run them on a desktop session:

    python examples/01_minimal.py

| # | file | adds |
|---|------|------|
| 01 | [`01_minimal.py`](01_minimal.py) | `run_file_dialog()` with defaults; reading `DialogResult` |
| 02 | [`02_buttons_filetypes.py`](02_buttons_filetypes.py) | `title`/`subtitle`, custom `buttons` (every `PickKind`), `FileType` filters, `default_dir`, `result.kind` |
| 03 | [`03_theme_info.py`](03_theme_info.py) | a custom `Theme` + an `info` card (list of sections, themed helpers) |
| 04 | [`04_slots_options.py`](04_slots_options.py) | `top_draw`, `options_draw`/`options_label`, `on_select`/`on_cancel`, `quit_label` |
| 05 | [`05_recent_files.py`](05_recent_files.py) | built-in `JsonPreferenceStore` (recents + start-dir seeding) |
| 06 | [`06_embedded_app.py`](06_embedded_app.py) | embed the `FileDialog` widget in your own runner; `header_draw`/`footer_draw`, `take_result()` |

Every example exposes a `build_config()` so the same configs drive the
screenshot tooling shown in the [README](../README.md#examples). Regenerate the
images with:

    pip install -e ".[docs]"
    python scripts/capture_docs.py
