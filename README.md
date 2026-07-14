# imgui_data_loader

A themed, configurable **file / folder open dialog** for
[imgui-bundle](https://github.com/pthom/imgui_bundle).

It builds on the pieces imgui-bundle already ships —
[imgui](https://github.com/ocornut/imgui) and
[hello_imgui](https://github.com/pthom/hello_imgui) for the UI, and
`portable_file_dialogs` for the **OS-native** file picker — and wraps them in a
small, styled **launcher window**: a title, your help/info content, and buttons
that open the native picker. Buttons, file types, theme, the info card, and an
options popup are all configurable. Pop it up one-shot to get back the path the
user picked, or embed the widget as one panel of a larger app.

<p align="center">
  <a href="#dialog_complex">
    <img src="docs/_images/examples/dialog_complex.png" alt="imgui_data_loader file dialog" width="360">
  </a>
</p>

## Install

```bash
pip install imgui_data_loader
```

The only dependency is `imgui-bundle` (which provides imgui, hello_imgui,
immapp, portable_file_dialogs and the FontAwesome icon font).

## Quick start

```python
from imgui_data_loader import run_file_dialog, FileDialogConfig

result = run_file_dialog(FileDialogConfig())   # default Open File(s) / Select Folder

if result:                      # truthy only for a real selection
    print(result.paths)         # list[str]
    print(result.path)          # first path, or None
else:
    print("cancelled")
```

`run_file_dialog` opens the window, blocks until the user picks something or
quits, and returns a `DialogResult`.

## Examples

Runnable scripts in [`examples/`](examples/) — run them on a desktop session
(`python examples/dialog_minimal.py`). The full source for `dialog_complex` is
[at the bottom of this README](#dialog_complex).

| name | file | shows |
|------|------|-------|
| dialog_minimal | [`dialog_minimal.py`](examples/dialog_minimal.py) | the one call — `run_file_dialog()` with defaults, reading the `DialogResult` |
| dialog_complex | [`dialog_complex.py`](examples/dialog_complex.py) | a microscopy loader wired to everything: custom `buttons` + `FileType` filters, a dataset picker and notes field, a custom `Theme`, an `info` card, a load-options popup, recent-files history, and result callbacks |
| dialog_themes | [`dialog_themes.py`](examples/dialog_themes.py) | a light `Theme` in a resized window, with hand-placed UI — an anchored popup (`set_next_window_pos`) and a right-aligned action via the cursor API, through `footer_draw` |

## What you can do with imgui is endless

The callback slots (`header_draw`, `top_draw`, `info`, `options_draw`,
`footer_draw`) all run inside a live imgui frame, so any widget **bundled with
imgui-bundle** works — animated toggles, rotary knobs, spinners, markdown,
command palettes, cool bars, and the rest. Pair them with the library's themed
helpers (`center_text`, `icon_button`, `push_button_style`, …) and `dlg.theme`
to match the styling. For a sense of just how far plain imgui goes, browse
[this long thread of community examples](https://github.com/ocornut/imgui/issues/3488#issuecomment-698634017).

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
| `ini_path` | `~/.config/imgui_data_loader/…` | where the layout `.ini` is saved |
| `assets_folder` | imgui-bundle's | folder providing the icon font |
| `persistence` | `None` | a `PreferenceStore` |
| `on_select`, `on_cancel` | `None` | result callbacks |

## Notes

- Buttons open the **OS-native** dialog, so a desktop session is required (no
  in-window file browser).
- Icons come from FontAwesome 6 (**Solid** only), which ships inside
  imgui-bundle; a few non-solid glyphs render as a blank box — pick a solid icon
  if one shows empty.
- Draw callbacks run inside an active imgui frame — only call imgui from them.

## License

MIT

---

<a id="dialog_complex"></a>

## The `dialog_complex` example

The screenshot at the top of this README. A microscopy loader that pulls in
every feature at once — custom buttons and filters, a dataset picker and a notes
field (both sized to match the button width), a custom theme, an info card, a
load-options popup, recent-files history, and callbacks. Full source, also in
[`examples/dialog_complex.py`](examples/dialog_complex.py):

```python
from imgui_bundle import hello_imgui
from imgui_bundle import icons_fontawesome_6 as fa
from imgui_bundle import imgui
from imgui_data_loader import (
    ButtonSpec, DialogResult, FileDialogConfig, FileType, JsonPreferenceStore,
    PickKind, Theme, center_next_item, center_text, run_file_dialog,
)

STORE = JsonPreferenceStore()          # ~/.config/imgui_data_loader/recent.json
STATE = {"dataset": 1, "notes": "Sample A2 · 40x · GCaMP6f",
         "recurse": True, "downsample": 1}
DATASETS = ["2D image", "3D volume", "Time series"]
IMAGES = [FileType("TIFF", "*.tif *.tiff"), FileType("All Files", "*")]


def _row_width():
    # the same width the dialog gives its buttons, so the row lines up with them
    return min(imgui.get_content_region_avail().x - hello_imgui.em_size(2),
               hello_imgui.em_size(16))


def controls(dlg):                     # top_draw: dataset picker + notes
    width = _row_width()
    center_next_item(width)
    _, STATE["dataset"] = imgui.combo("##dataset", STATE["dataset"], DATASETS)
    center_next_item(width)
    _, STATE["notes"] = imgui.input_text_multiline(
        "##notes", STATE["notes"], imgui.ImVec2(width, hello_imgui.em_size(3.2)))


def info(dlg):                         # info card contents
    center_text("Supported formats", dlg.theme.accent)
    imgui.bullet_text("TIFF / Zarr / HDF5")
    if STORE.recent():
        imgui.text_colored(dlg.theme.text_dim, "Recent:")
        for path in STORE.recent()[:3]:
            imgui.bullet_text(path)


def options(dlg):                      # options_draw: the load-options popup
    _, STATE["recurse"]    = imgui.checkbox("Recurse into subfolders", STATE["recurse"])
    imgui.set_next_item_width(140)
    _, STATE["downsample"] = imgui.slider_int("Downsample", STATE["downsample"], 1, 8)


def on_select(result: DialogResult):
    print(DATASETS[STATE["dataset"]], STATE["notes"], result.paths)


run_file_dialog(FileDialogConfig(
    title="Microscopy Loader",
    subtitle="load an acquisition to begin",
    theme=Theme.dark().replace(accent=(0.20, 0.75, 0.70, 1.0)),
    persistence=STORE,                 # seeds start dir + records selections
    top_draw=controls,
    info=info,
    options_draw=options,
    options_label="Load options",
    quit_label="Close",
    on_select=on_select,
    on_cancel=lambda: print("cancelled"),
    buttons=[
        ButtonSpec("Open image(s)", PickKind.OPEN_FILE, icon=fa.ICON_FA_FILE_IMAGE,
                   multiselect=True, filetypes=IMAGES),
        ButtonSpec("Open a folder", PickKind.SELECT_FOLDER, icon=fa.ICON_FA_FOLDER_OPEN),
        ButtonSpec("Export as…", PickKind.SAVE_FILE, icon=fa.ICON_FA_FLOPPY_DISK,
                   filetypes=[FileType("Zarr", "*.zarr")]),
    ],
))
```
