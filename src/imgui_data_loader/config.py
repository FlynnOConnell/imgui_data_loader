"""Configuration objects for the file dialog.

None of these require an active imgui context, so a config can be built and
inspected anywhere (``_default_buttons`` only imports icon *string constants*).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Sequence,
    Union,
)

from .theme import Theme

if TYPE_CHECKING:  # pragma: no cover
    from .dialog import FileDialog
    from .persistence import PreferenceStore

# A draw callback may take the FileDialog instance or nothing; both are
# accepted (see widgets.call_draw for the arity handling).
DrawCallback = Callable[..., None]


class PickKind(str, Enum):
    """What a button asks the OS picker for."""

    OPEN_FILE = "open_file"
    SELECT_FOLDER = "select_folder"
    SAVE_FILE = "save_file"


@dataclass
class FileType:
    """A named file filter, e.g. ``FileType("Images", "*.tif *.png")``.

    ``patterns`` is a space-separated glob string (portable_file_dialogs
    format). A list/tuple of patterns is also accepted and joined.
    """

    name: str
    patterns: str = "*"

    def __post_init__(self) -> None:
        if isinstance(self.patterns, (list, tuple)):
            self.patterns = " ".join(self.patterns)


def flatten_filters(filetypes: Sequence[FileType]) -> List[str]:
    """Flatten ``[FileType, ...]`` into pfd's ``[name, patterns, ...]`` list."""
    out: List[str] = []
    for ft in filetypes:
        out.append(ft.name)
        out.append(ft.patterns)
    return out


@dataclass
class ButtonSpec:
    """One picker button on the dialog.

    Parameters
    ----------
    label : str
        Button text.
    kind : PickKind
        Which native picker to open.
    icon : str
        A FontAwesome 6 icon character (e.g. ``fa.ICON_FA_FOLDER_OPEN``);
        optional.
    tooltip : str
        Hover tooltip.
    multiselect : bool
        For ``OPEN_FILE`` only: allow selecting several files.
    filetypes : list[FileType] | None
        Overrides the dialog-wide ``filetypes`` for this button.
    title : str | None
        Native dialog window title (defaults to ``label``).
    """

    label: str
    kind: PickKind = PickKind.OPEN_FILE
    icon: str = ""
    tooltip: str = ""
    multiselect: bool = False
    filetypes: Optional[List[FileType]] = None
    title: Optional[str] = None


@dataclass
class DialogResult:
    """Outcome of the dialog.

    ``paths`` holds the selected path(s); it is empty when the user quit /
    cancelled. ``bool(result)`` is True only for a real, non-empty selection.
    """

    paths: List[str] = field(default_factory=list)
    kind: Optional[PickKind] = None
    cancelled: bool = False

    @property
    def path(self) -> Optional[str]:
        """First selected path, or None."""
        return self.paths[0] if self.paths else None

    def __bool__(self) -> bool:
        return bool(self.paths) and not self.cancelled


def _default_buttons() -> List[ButtonSpec]:
    from imgui_bundle import icons_fontawesome_6 as fa

    return [
        ButtonSpec(
            "Open File(s)",
            PickKind.OPEN_FILE,
            icon=fa.ICON_FA_FILE_IMAGE,
            tooltip="Select one or more files",
            multiselect=True,
        ),
        ButtonSpec(
            "Select Folder",
            PickKind.SELECT_FOLDER,
            icon=fa.ICON_FA_FOLDER_OPEN,
            tooltip="Select a folder",
        ),
    ]


@dataclass
class FileDialogConfig:
    """Everything the dialog can be told to do.

    All fields have sensible defaults; the empty ``FileDialogConfig()`` gives
    an "Open File(s)" + "Select Folder" launcher.

    Content slots (``header_draw``, ``top_draw``, ``info``, ``options_draw``,
    ``footer_draw``) are callbacks that draw arbitrary imgui inside the dialog.
    Each callback may accept the :class:`FileDialog` instance or no argument.
    """

    # --- header / branding ---
    title: str = "Open Data"
    subtitle: str = ""

    # --- picker buttons ---
    buttons: List[ButtonSpec] = field(default_factory=_default_buttons)
    filetypes: List[FileType] = field(
        default_factory=lambda: [FileType("All Files", "*")]
    )
    default_dir: str = ""

    # --- look ---
    theme: Theme = field(default_factory=Theme.dark)

    # --- content slots (each: fn(dialog) or fn()) ---
    header_draw: Optional[DrawCallback] = None
    top_draw: Optional[DrawCallback] = None
    info: Union[DrawCallback, Sequence[DrawCallback], None] = None
    options_draw: Optional[DrawCallback] = None
    footer_draw: Optional[DrawCallback] = None

    # --- footer labels / behavior ---
    options_label: str = "Options"
    show_options_button: bool = True
    show_quit_button: bool = True
    quit_label: str = "Quit"
    quit_on_escape: bool = True
    close_on_select: bool = True

    # --- window / harness (used by run_file_dialog) ---
    window_title: Optional[str] = None
    window_size: tuple = (360, 720)
    resizable: bool = True
    ini_path: Optional[str] = None
    assets_folder: Optional[str] = None

    # --- integrations ---
    persistence: "Optional[PreferenceStore]" = None
    on_select: Optional[Callable[[DialogResult], None]] = None
    on_cancel: Optional[Callable[[], None]] = None

    def info_callbacks(self) -> List[DrawCallback]:
        """Normalize ``info`` to a list of callbacks."""
        if self.info is None:
            return []
        if callable(self.info):
            return [self.info]
        return list(self.info)
