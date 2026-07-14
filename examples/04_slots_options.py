"""04 - Content slots + options popup + result callbacks.

New vs 03:
  * top_draw   - a widget row between the header and the buttons (a "mode" combo)
  * options_draw / options_label - an Options popup with live controls
  * on_select / on_cancel - react to the outcome without inspecting the return
  * quit_label - rename the Quit button

    python examples/04_slots_options.py
"""

from dataclasses import dataclass, field
from typing import List

from imgui_bundle import imgui

from imgui_data_loader import DialogResult, FileDialogConfig, run_file_dialog


@dataclass
class Settings:
    mode_index: int = 0
    modes: List[str] = field(
        default_factory=lambda: ["2D", "3D volume", "Time series"]
    )
    recurse: bool = True
    downsample: int = 1


SETTINGS = Settings()


def mode_row(dlg) -> None:
    imgui.set_next_item_width(imgui.get_content_region_avail().x)
    _, SETTINGS.mode_index = imgui.combo(
        "##mode", SETTINGS.mode_index, SETTINGS.modes
    )
    if imgui.is_item_hovered():
        imgui.set_tooltip("How to interpret the data you open")


def options(dlg) -> None:
    _, SETTINGS.recurse = imgui.checkbox("Recurse into subfolders", SETTINGS.recurse)
    imgui.set_next_item_width(140)
    _, SETTINGS.downsample = imgui.slider_int("Downsample", SETTINGS.downsample, 1, 8)


def on_select(result: DialogResult) -> None:
    print(
        f"[on_select] mode={SETTINGS.modes[SETTINGS.mode_index]} "
        f"recurse={SETTINGS.recurse} downsample={SETTINGS.downsample}"
    )
    print("[on_select]", result.paths)


def on_cancel() -> None:
    print("[on_cancel] user quit")


def build_config() -> FileDialogConfig:
    return FileDialogConfig(
        title="Volume Loader",
        subtitle="mode + options",
        top_draw=mode_row,
        options_draw=options,
        options_label="Load options",
        quit_label="Close",
        on_select=on_select,
        on_cancel=on_cancel,
    )


def main() -> None:
    run_file_dialog(build_config())  # outcome handled by the callbacks


if __name__ == "__main__":
    main()
