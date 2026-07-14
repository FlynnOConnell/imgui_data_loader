"""The :class:`FileDialog` widget.

Render it inside a hello_imgui / immapp frame (set ``params.callbacks.show_gui
= dialog.render``). Buttons trigger the OS-native picker via
``portable_file_dialogs``; when a selection completes it lands on
:attr:`FileDialog.result`.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from imgui_bundle import (
    hello_imgui,
    icons_fontawesome_6 as fa,
    imgui,
    imgui_ctx,
    portable_file_dialogs as pfd,
)

from .config import (
    ButtonSpec,
    DialogResult,
    FileDialogConfig,
    FileType,
    PickKind,
    flatten_filters,
)
from .theme import Theme, to_vec4
from .widgets import (
    call_draw,
    center_next_item,
    center_text,
    icon_button,
    pop_button_style,
    push_button_style,
    wrapped_tooltip,
)


class FileDialog:
    """A themed, configurable file/folder open dialog.

    Parameters
    ----------
    config : FileDialogConfig | None
        Behavior and content. Defaults to a plain "Open File(s) / Select
        Folder" launcher.
    """

    def __init__(self, config: Optional[FileDialogConfig] = None):
        self.config = config or FileDialogConfig()
        self._pending = None  # active portable_file_dialogs handle
        self._pending_kind: Optional[PickKind] = None
        self._result: Optional[DialogResult] = None
        self._open_options = False

    # ------------------------------------------------------------------
    # public surface
    # ------------------------------------------------------------------
    @property
    def theme(self) -> Theme:
        return self.config.theme

    @property
    def result(self) -> Optional[DialogResult]:
        """Last completed result (peek; does not clear)."""
        return self._result

    def take_result(self) -> Optional[DialogResult]:
        """Return the last result and clear it (for embedded per-frame polling)."""
        r, self._result = self._result, None
        return r

    def open_options(self) -> None:
        """Programmatically open the Options popup on the next frame."""
        self._open_options = True

    def pick(self, button: ButtonSpec) -> None:
        """Open the OS-native picker described by ``button``.

        This is what a built-in button does when clicked. Call it from your own
        content slot when you draw custom buttons instead of using
        ``config.buttons`` — the completed selection lands on
        :attr:`result` / ``on_select`` exactly the same way.
        """
        self._launch(button)

    def apply_host_theme(self, runner_params) -> None:
        """Point the hosting window's background at ``theme.bg``.

        The dialog colors its own frames every frame, but the window *behind*
        them is painted from the imgui style's ``window_bg`` before ``render``
        runs — so a light theme would otherwise sit on hello_imgui's default
        dark backdrop. Call this once on the ``RunnerParams`` before running
        (``run_file_dialog`` does it for you); any existing
        ``setup_imgui_style`` callback is preserved.
        """
        bg = to_vec4(self.theme.bg)
        runner_params.imgui_window_params.background_color = bg
        prev = runner_params.callbacks.setup_imgui_style

        def _setup_style():
            if callable(prev):
                prev()
            imgui.get_style().set_color_(imgui.Col_.window_bg, bg)

        runner_params.callbacks.setup_imgui_style = _setup_style

    def cancel(self) -> None:
        """Finish with an empty, cancelled result (as the Quit button does)."""
        self._finish(DialogResult(paths=[], kind=None, cancelled=True))

    # ------------------------------------------------------------------
    # native picker plumbing
    # ------------------------------------------------------------------
    def _start_dir(self) -> str:
        if self.config.default_dir:
            return str(self.config.default_dir)
        store = self.config.persistence
        if store is not None:
            try:
                d = store.default_dir()
                if d:
                    return str(d)
            except Exception:
                pass
        return str(Path.home())

    def _filters_for(self, btn: ButtonSpec) -> List[str]:
        fts = btn.filetypes if btn.filetypes is not None else self.config.filetypes
        return flatten_filters(fts or [FileType("All Files", "*")])

    def _launch(self, btn: ButtonSpec) -> None:
        start = self._start_dir()
        title = btn.title or btn.label
        if btn.kind == PickKind.OPEN_FILE:
            opt = pfd.opt.multiselect if btn.multiselect else pfd.opt.none
            self._pending = pfd.open_file(title, start, self._filters_for(btn), opt)
        elif btn.kind == PickKind.SELECT_FOLDER:
            self._pending = pfd.select_folder(title, start)
        elif btn.kind == PickKind.SAVE_FILE:
            self._pending = pfd.save_file(title, start, self._filters_for(btn))
        else:
            return
        self._pending_kind = btn.kind

    def _poll(self) -> None:
        if self._pending is None or not self._pending.ready():
            return
        raw = self._pending.result()
        kind = self._pending_kind
        self._pending = None
        self._pending_kind = None
        if isinstance(raw, list):
            paths = [p for p in raw if p]
        elif raw:
            paths = [raw]
        else:
            paths = []
        # An empty result means the user cancelled the native picker itself;
        # stay open so they can try another button.
        if paths:
            self._finish(DialogResult(paths=paths, kind=kind, cancelled=False))

    def _finish(self, result: DialogResult) -> None:
        self._result = result
        cfg = self.config
        if not result.cancelled:
            if cfg.persistence is not None:
                try:
                    cfg.persistence.record_selection(result)
                except Exception:
                    pass
            if cfg.on_select is not None:
                cfg.on_select(result)
            if cfg.close_on_select:
                self._request_exit()
        else:
            if cfg.on_cancel is not None:
                cfg.on_cancel()
            self._request_exit()

    @staticmethod
    def _request_exit() -> None:
        try:
            hello_imgui.get_runner_params().app_shall_exit = True
        except Exception:
            pass

    # ------------------------------------------------------------------
    # rendering
    # ------------------------------------------------------------------
    def render(self) -> None:
        """Draw one frame of the dialog. Use as ``callbacks.show_gui``."""
        theme = self.theme
        imgui.push_style_color(imgui.Col_.window_bg, to_vec4(theme.bg))
        imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(0, 0, 0, 0))
        imgui.push_style_color(imgui.Col_.text, to_vec4(theme.text))
        imgui.push_style_color(imgui.Col_.border, to_vec4(theme.border))
        imgui.push_style_color(imgui.Col_.separator, to_vec4(theme.separator))
        imgui.push_style_color(imgui.Col_.frame_bg, to_vec4(theme.frame_bg))
        imgui.push_style_color(imgui.Col_.frame_bg_hovered, to_vec4(theme.frame_bg_hovered))
        imgui.push_style_color(imgui.Col_.check_mark, to_vec4(theme.accent))
        imgui.push_style_var(imgui.StyleVar_.window_padding, hello_imgui.em_to_vec2(1.0, 0.8))
        imgui.push_style_var(imgui.StyleVar_.frame_padding, hello_imgui.em_to_vec2(0.6, 0.4))
        imgui.push_style_var(imgui.StyleVar_.item_spacing, hello_imgui.em_to_vec2(0.6, 0.4))
        imgui.push_style_var(imgui.StyleVar_.frame_rounding, theme.frame_rounding)

        with imgui_ctx.begin_child(
            "##idl_main",
            size=imgui.ImVec2(0, 0),
            window_flags=imgui.WindowFlags_.no_scrollbar,
        ):
            imgui.push_id("imgui_data_loader")

            self._draw_header()

            imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))
            imgui.separator()
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))

            if self.config.top_draw is not None:
                call_draw(self.config.top_draw, self)
                imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))

            self._draw_buttons()
            self._draw_info_card()
            self._draw_options_popup()
            self._poll()
            self._draw_footer()

            imgui.pop_id()

        imgui.pop_style_var(4)
        imgui.pop_style_color(8)

    def _button_width(self) -> float:
        avail_w = imgui.get_content_region_avail().x
        return min(avail_w - hello_imgui.em_size(2), hello_imgui.em_size(16))

    def _draw_header(self) -> None:
        if self.config.header_draw is not None:
            call_draw(self.config.header_draw, self)
            return
        imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))
        center_text(self.config.title, self.theme.accent)
        if self.config.subtitle:
            center_text(self.config.subtitle, self.theme.text_dim)

    def _draw_buttons(self) -> None:
        btn_w = self._button_width()
        btn_h = hello_imgui.em_size(1.8)
        for i, btn in enumerate(self.config.buttons):
            center_next_item(btn_w)
            imgui.push_id(i)
            if icon_button(
                btn.icon,
                btn.label,
                imgui.ImVec2(btn_w, btn_h),
                theme=self.theme,
                tooltip=btn.tooltip,
            ):
                self._launch(btn)
            imgui.pop_id()
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))

    def _draw_info_card(self) -> None:
        callbacks = self.config.info_callbacks()
        if not callbacks:
            return
        theme = self.theme
        imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))
        card_w = self._button_width()
        center_next_item(card_w)

        # Transparent fill: the card shows the dialog background, leaving only
        # its border — so it reads with the same weight as the outlined buttons.
        imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(0, 0, 0, 0))
        imgui.push_style_var(imgui.StyleVar_.child_rounding, theme.child_rounding)
        imgui.push_style_var(imgui.StyleVar_.cell_padding, hello_imgui.em_to_vec2(0.4, 0.2))

        child_flags = imgui.ChildFlags_.borders | imgui.ChildFlags_.auto_resize_y
        window_flags = imgui.WindowFlags_.no_scrollbar
        with imgui_ctx.begin_child(
            "##idl_info",
            size=imgui.ImVec2(card_w, 0),
            child_flags=child_flags,
            window_flags=window_flags,
        ):
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))
            imgui.indent(hello_imgui.em_size(0.6))
            for j, cb in enumerate(callbacks):
                if j:
                    imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))
                imgui.push_id(1000 + j)
                call_draw(cb, self)
                imgui.pop_id()
            imgui.unindent(hello_imgui.em_size(0.6))
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))

        imgui.pop_style_var(2)
        imgui.pop_style_color()

    def _draw_options_popup(self) -> None:
        if self.config.options_draw is None:
            return
        if self._open_options:
            imgui.open_popup("##idl_options")
            self._open_options = False
        # Anchor the popup to the dialog's center. Without this, imgui places it
        # at the cursor/mouse point, which drifts far down a tall window. Cond
        # "appearing" positions it only when it opens, so it can still be dragged.
        if imgui.is_popup_open("##idl_options"):
            wp, ws = imgui.get_window_pos(), imgui.get_window_size()
            center = imgui.ImVec2(wp.x + ws.x * 0.5, wp.y + ws.y * 0.5)
            imgui.set_next_window_pos(center, imgui.Cond_.appearing, imgui.ImVec2(0.5, 0.5))
        if not imgui.begin_popup("##idl_options", imgui.WindowFlags_.always_auto_resize):
            return
        try:
            imgui.text_colored(
                to_vec4(self.theme.accent),
                f"{fa.ICON_FA_GEARS}  {self.config.options_label}",
            )
            imgui.separator()
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.2))
            call_draw(self.config.options_draw, self)
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))
            if imgui.button("Close", imgui.ImVec2(hello_imgui.em_size(6), 0)):
                imgui.close_current_popup()
        finally:
            imgui.end_popup()

    def _draw_footer(self) -> None:
        cfg = self.config
        if cfg.footer_draw is not None:
            imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))
            call_draw(cfg.footer_draw, self)
            self._handle_escape()
            return

        show_options = cfg.options_draw is not None and cfg.show_options_button
        show_quit = cfg.show_quit_button
        if not (show_options or show_quit):
            self._handle_escape()
            return

        imgui.dummy(hello_imgui.em_to_vec2(0, 0.3))
        theme = self.theme
        style = imgui.get_style()
        # size each button to its (icon + label) text so custom labels don't clip
        opt_text = f"{fa.ICON_FA_GEARS}  {cfg.options_label}"
        quit_text = f"{fa.ICON_FA_XMARK}  {cfg.quit_label}"
        pad = style.frame_padding.x * 2 + hello_imgui.em_size(0.6)
        min_w = hello_imgui.em_size(4.5)
        opt_w = max(imgui.calc_text_size(opt_text).x + pad, min_w)
        quit_w = max(imgui.calc_text_size(quit_text).x + pad, min_w)
        spacing = style.item_spacing.x
        row_w = 0.0
        if show_options:
            row_w += opt_w
        if show_quit:
            row_w += quit_w
        if show_options and show_quit:
            row_w += spacing
        center_next_item(row_w)

        btn_h = hello_imgui.em_size(1.5)
        push_button_style(theme, primary=False)
        if show_options:
            if imgui.button(opt_text, imgui.ImVec2(opt_w, btn_h)):
                self._open_options = True
            if imgui.is_item_hovered():
                wrapped_tooltip(cfg.options_label)
            if show_quit:
                imgui.same_line()
        if show_quit:
            if imgui.button(quit_text, imgui.ImVec2(quit_w, btn_h)):
                self.cancel()
        pop_button_style()

        self._handle_escape()

    def _handle_escape(self) -> None:
        if self.config.quit_on_escape and imgui.is_key_pressed(imgui.Key.escape):
            self.cancel()
