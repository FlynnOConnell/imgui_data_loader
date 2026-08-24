# Architecture

Internal notes for contributors to `imgui_data_loader`.

## What this is

`imgui_data_loader` is a small, installable library that renders a themed, configurable **file/folder open dialog** for [imgui-bundle](https://github.com/pthom/imgui_bundle). It is a styled *launcher window* (title, info card, buttons) whose buttons open the **OS-native** file picker via `portable_file_dialogs` — there is no in-window file browser, so a real desktop session is required to actually pick files. The only runtime dependency is `imgui-bundle` (which bundles imgui, hello_imgui, immapp, portable_file_dialogs, and the FontAwesome 6 font).

## Commands

```bash
pip install -e '.[dev]'      # editable install with pytest
pytest                       # run the full suite (testpaths=tests)
pytest tests/test_config.py  # one file
pytest tests/test_headless_render.py::test_ini_path_is_configurable  # one test
```

There is no configured linter/formatter. The package ships `py.typed`, so keep type hints intact.

## Architecture

The package has two usage modes, which drives the module split:

- **Embedded** — construct a `FileDialog(config)` and call `dlg.render()` inside your own hello_imgui/immapp frame (`params.callbacks.show_gui`). Poll `dlg.take_result()` each frame, or set `config.on_select`.
- **One-shot** — `run_file_dialog(config)` (in `runner.py`) builds the window, owns the immapp run loop, blocks, and returns a `DialogResult`. It exits the loop by setting `app_shall_exit` on selection/cancel (`close_on_select`).

Module responsibilities:

- `config.py` — all pure data (`FileDialogConfig`, `ButtonSpec`, `FileType`, `PickKind`, `DialogResult`). **Deliberately importable without an active imgui context** — no imgui state is touched at construction time (the default-buttons factory imports only icon *string constants*). Keep it that way. `DialogResult.__bool__` is True only for a real, non-empty, non-cancelled selection — callers rely on `if result:`.
- `dialog.py` — the `FileDialog` widget: all rendering (`render()` and the `_draw_*` methods) plus the native-picker state machine. A button click calls `_launch()` (opens a `portable_file_dialogs` handle into `self._pending`); `_poll()` runs every frame and completes into `_finish()` when the handle is `ready()`. An **empty** native result means the user cancelled the OS picker — the dialog stays open rather than finishing.
- `theme.py` — `Theme`, a frozen dataclass of `(r,g,b,a)` tuples plus rounding knobs. `Theme.dark()`/`Theme.light()`/`.replace(...)`. Colors are converted to `imgui.ImVec4` lazily at draw time via `to_vec4`, so themes are context-free too.
- `widgets.py` — standalone themed imgui helpers (`icon_button`, `center_text`, `wrapped_tooltip`, `push/pop_button_style`, …) reused by both the dialog internals and user callbacks. `call_draw` inspects a callback's signature so content slots accept either `fn(dialog)` or `fn()`.
- `persistence.py` — the `PreferenceStore` Protocol (`default_dir` / `recent` / `record_selection`) and a JSON-backed default. The dialog seeds the picker start dir from it and records selections; **all store calls in the dialog are wrapped in `try/except` and never fatal**.
- `_assets.py` — points hello_imgui at imgui-bundle's own bundled assets folder (for the FontAwesome font) and computes config/`.ini` paths under `$XDG_CONFIG_HOME/imgui_data_loader`. The library ships no fonts of its own.
- `runner.py` — the one-shot harness only. Note the `.ini` handling: hello_imgui otherwise drops the window-layout `.ini` in the cwd, so `run_file_dialog` pins it to an absolute path (`config.ini_path` or `default_ini_path()`) and creates the parent dir. It only fills `ini_filename` when unset, so an embedding app's choice wins.

Content is injected through **draw-callback slots** on the config (`header_draw`, `top_draw`, `info`, `options_draw`, `footer_draw`). These run *inside an active imgui frame* — they may only call imgui.

The bundled FontAwesome build is **Solid** only; a few glyph constants (e.g. `ICON_FA_IMAGES`, `ICON_FA_LAYER_GROUP`, `ICON_FA_PHOTO_FILM`) are regular-style and render as a blank box. Prefer solid icons (`ICON_FA_FILE_IMAGE`, `ICON_FA_CLONE`, `ICON_FA_COPY`, `ICON_FA_FOLDER_OPEN`, `ICON_FA_FLOPPY_DISK`, …).

## Documentation screenshots

`scripts/capture_docs.py` runs each example's real dialog in a hello_imgui window, reads back the framebuffer with `hello_imgui.final_app_window_screenshot()`, autocrops to content, and adds padding + a drop shadow. Each example exposes a module-level `CONFIG` so the same config drives both the runnable example and the screenshot. Needs a desktop session and the `[docs]` extra (pillow + numpy). Output lands in `examples/images/`.

## Testing notes

Rendering is exercised headlessly on hello_imgui's **null backend** (no window/GPU) — see `_null_runner_params()` in `tests/test_headless_render.py`. Two gotchas that pattern encodes: the null renderer needs `BackendFlags_.renderer_has_textures` set in `post_init` (imgui 1.92 asserts otherwise), and tests must route the `.ini` to a temp folder. If the backend can't init in the environment, these tests **skip** rather than fail, so a green run may mean "skipped" — check the output. Config/theme/persistence tests are pure and always run.
