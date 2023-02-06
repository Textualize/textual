from __future__ import annotations
import typing

from ..geometry import Spacing
from .._typing import Final

if typing.TYPE_CHECKING:
    from .types import EdgeType

VALID_VISIBILITY: Final[set[str]] = {"visible", "hidden"}
VALID_DISPLAY: Final[set[str]] = {"block", "none"}
VALID_BORDER: Final[set[EdgeType]] = {
    "none",
    "hidden",
    "ascii",
    "round",
    "blank",
    "solid",
    "double",
    "dashed",
    "heavy",
    "inner",
    "outer",
    "hkey",
    "vkey",
    "tall",
    "wide",
}
VALID_EDGE: Final[set[str]] = {"top", "right", "bottom", "left"}
VALID_LAYOUT: Final[set[str]] = {"vertical", "horizontal", "grid"}

VALID_BOX_SIZING: Final[set[str]] = {"border-box", "content-box"}
VALID_OVERFLOW: Final[set[str]] = {"scroll", "hidden", "auto"}
VALID_ALIGN_HORIZONTAL: Final[set[str]] = {"left", "center", "right"}
VALID_ALIGN_VERTICAL: Final[set[str]] = {"top", "middle", "bottom"}
VALID_TEXT_ALIGN: Final[set[str]] = {
    "start",
    "end",
    "left",
    "right",
    "center",
    "justify",
}
VALID_SCROLLBAR_GUTTER: Final[set[str]] = {"auto", "stable"}
VALID_STYLE_FLAGS: Final[set[str]] = {
    "b",
    "blink",
    "bold",
    "dim",
    "i",
    "italic",
    "none",
    "not",
    "o",
    "overline",
    "reverse",
    "strike",
    "u",
    "underline",
    "uu",
}


NULL_SPACING: Final[Spacing] = Spacing.all(0)
