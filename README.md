# imgui_data_loader

A themed, configurable **file / folder open dialog** for
[imgui-bundle](https://github.com/pthom/imgui_bundle). Drop it into a
[hello_imgui](https://github.com/pthom/hello_imgui) / `immapp` app, or use the
one-shot helper to pop up a launcher window and get back the path the user
picked.

It's a small, styled **launcher window** — a title, your help/info content, and
buttons that open the **OS-native** file picker (via
`portable_file_dialogs`). Everything is configurable: buttons, file types,
theme, the info card, and an options popup.

<!-- screenshot placeholder -->

## Install

```bash
pip install imgui_data_loader
```

The only dependency is `imgui-bundle` (which provides imgui, hello_imgui,
immapp, portable_file_dialogs and the FontAwesome icon font).

## Quick start — one-shot

```python
from imgui_data_loader import run_file_dialog, FileDialogConfig, FileType

result = run_file_dialog(FileDialogConfig(
    title="My App",
    subtitle="Open a dataset",
    filetypes=[
        FileType("Images", "*.tif *.tiff *.png *.jpg"),
        FileType("All Files", "*"),
    ],
))

if result:                      # truthy only for a real selection
    print(result.paths)         # list[str]
    print(result.path)          # first path, or None
else:
    print("cancelled")
```

`run_file_dialog` opens the window, blocks until the user picks something or
quits, and returns a `DialogResult`.

## Customize the buttons and file types

By default you get **Open File(s)** and **Select Folder**. Replace them with
whatever mix of file / folder / save buttons you need:

```python
from imgui_data_loader import (
    run_file_dialog, FileDialogConfig, ButtonSpec, PickKind, FileType,
)
from imgui_bundle import icons_fontawesome_6 as fa

cfg = FileDialogConfig(
    title="Importer",
    buttons=[
        ButtonSpec("Open TIFF", PickKind.OPEN_FILE, icon=fa.ICON_FA_FILE_IMAGE,
                   multiselect=True, filetypes=[FileType("TIFF", "*.tif *.tiff")]),
        ButtonSpec("Open project folder", PickKind.SELECT_FOLDER,
                   icon=fa.ICON_FA_FOLDER_OPEN),
        ButtonSpec("Save as…", PickKind.SAVE_FILE, icon=fa.ICON_FA_FLOPPY_DISK,
                   filetypes=[FileType("Zarr", "*.zarr")]),
    ],
)
result = run_file_dialog(cfg)
print(result.kind, result.paths)   # result.kind tells you which button fired
```

## Add help text / an info card

`info` is one callback (or a list of them) drawn inside a rounded card below
the buttons. Use plain imgui plus the bundled helpers to match the styling:

```python
from imgui_bundle import imgui
from imgui_data_loader import (
    run_file_dialog, FileDialogConfig, text_wrapped_colored,
)

def formats_help(dlg):                 # callback gets the FileDialog (optional arg)
    imgui.text_colored(dlg.theme.accent, "Supported formats")
    imgui.bullet_text("TIFF / OME-TIFF")
    imgui.bullet_text("Zarr, HDF5, NumPy")
    text_wrapped_colored(dlg.theme.text_dim,
                         "Folders are opened as a stack of the files inside.")

run_file_dialog(FileDialogConfig(title="Loader", info=formats_help))
```

A zero-argument callback works too (`def formats_help(): ...`).

## Add an Options popup

Set `options_draw` and an **Options** button appears next to Quit; clicking it
opens a popup that renders your callback. Draw any imgui you like:

```python
from imgui_bundle import imgui

state = {"recursive": True, "cache": False}

def options(dlg):
    _, state["recursive"] = imgui.checkbox("Search subfolders", state["recursive"])
    _, state["cache"]     = imgui.checkbox("Use cache", state["cache"])

run_file_dialog(FileDialogConfig(title="Loader", options_draw=options))
```

## Theme it

`Theme` is a dataclass of RGBA tuples. Start from `Theme.dark()` (default) or
`Theme.light()` and override any color:

```python
from imgui_data_loader import FileDialogConfig, Theme

cfg = FileDialogConfig(
    theme=Theme.dark().replace(accent=(0.85, 0.35, 0.55, 1.0)),
)
```

## Remember recent files

Pass a `PreferenceStore`. The included `JsonPreferenceStore` seeds the picker's
start directory from the last used one and records selections to a JSON file:

```python
from imgui_data_loader import run_file_dialog, FileDialogConfig, JsonPreferenceStore

store = JsonPreferenceStore()          # ~/.config/imgui_data_loader/recent.json
run_file_dialog(FileDialogConfig(title="Loader", persistence=store))
print(store.recent())
```

Implement the three-method `PreferenceStore` protocol yourself to back it with
anything (a database, your app's settings, …).

## Embed it in your own app

Render the `FileDialog` widget inside an existing `immapp` / hello_imgui loop
instead of using the one-shot runner. Set `close_on_select=False` and poll
`take_result()` each frame:

```python
from imgui_bundle import hello_imgui, immapp
from imgui_data_loader import FileDialog, FileDialogConfig

dlg = FileDialog(FileDialogConfig(title="Loader", close_on_select=False))

def gui():
    dlg.render()
    result = dlg.take_result()         # None until the user picks
    if result:
        load(result.paths)             # your code

params = hello_imgui.RunnerParams()
params.callbacks.show_gui = gui
immapp.run(params)
```

Or react via a callback without polling: `FileDialogConfig(on_select=lambda r: load(r.paths))`.

## Configuration reference

`FileDialogConfig` fields:

| field | default | purpose |
|-------|---------|---------|
| `title`, `subtitle` | `"Open Data"`, `""` | header text |
| `buttons` | Open File(s) + Select Folder | list of `ButtonSpec` |
| `filetypes` | `[All Files]` | default filters for file/save buttons |
| `default_dir` | `""` | picker start dir (else persistence, else `~`) |
| `theme` | `Theme.dark()` | colors |
| `header_draw` | `None` | replace the title/subtitle block |
| `top_draw` | `None` | content between header and buttons |
| `info` | `None` | callback(s) drawn in the info card |
| `options_draw` | `None` | Options popup content (also toggles the button) |
| `footer_draw` | `None` | replace the Options/Quit row |
| `options_label` | `"Options"` | popup + button label |
| `show_options_button` | `True` | show Options (needs `options_draw`) |
| `show_quit_button`, `quit_label` | `True`, `"Quit"` | Quit button |
| `quit_on_escape` | `True` | Esc cancels |
| `close_on_select` | `True` | exit the run loop after a pick (one-shot mode) |
| `window_title`, `window_size`, `resizable` | — | OS window (one-shot) |
| `ini_path` | `~/.config/imgui_data_loader/…` | where the layout `.ini` is saved (see below) |
| `assets_folder` | imgui-bundle's | folder providing the icon font |
| `persistence` | `None` | a `PreferenceStore` |
| `on_select`, `on_cancel` | `None` | result callbacks |

## Where the layout `.ini` goes

hello_imgui persists window layout to a small `.ini`. By default `run_file_dialog`
writes it to an **absolute** path under your config dir —
`~/.config/imgui_data_loader/file_dialog.ini` (honoring `$XDG_CONFIG_HOME`) — so it
never lands in the current working directory. Change it with:

```python
run_file_dialog(FileDialogConfig(title="…", ini_path="/path/to/my_dialog.ini"))
```

The parent directory is created if needed. When you **embed** the dialog with your
own runner, set `params.ini_filename` (and optionally `params.ini_folder_type`)
yourself — `run_file_dialog` only fills it in when you leave it unset.

## Notes

- Buttons open the **OS-native** dialog, so a desktop session is required (no
  in-window file browser).
- Icons come from FontAwesome 6, which ships inside imgui-bundle;
  `run_file_dialog` points hello_imgui at that font automatically. When
  embedding, make sure your app's assets folder provides it (or pass
  `assets_folder`).
- Draw callbacks run inside an active imgui frame — only call imgui from them.

## License

MIT
