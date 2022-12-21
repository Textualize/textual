from __future__ import annotations
import typing

from ..geometry import Spacing
from .._typing import Final

if typing.TYPE_CHECKING:
    from .types import EdgeType

VALID_VISIBILITY: Final = {"visible", "hidden"}
VALID_DISPLAY: Final = {"block", "none"}
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
VALID_EDGE: Final = {"top", "right", "bottom", "left"}
VALID_LAYOUT: Final = {"vertical", "horizontal", "grid"}

VALID_BOX_SIZING: Final = {"border-box", "content-box"}
VALID_OVERFLOW: Final = {"scroll", "hidden", "auto"}
VALID_ALIGN_HORIZONTAL: Final = {"left", "center", "right"}
VALID_ALIGN_VERTICAL: Final = {"top", "middle", "bottom"}
VALID_TEXT_ALIGN: Final = {"start", "end", "left", "right", "center", "justify"}
VALID_SCROLLBAR_GUTTER: Final = {"auto", "stable"}
VALID_STYLE_FLAGS: Final = {
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

NULL_SPACING: Final = Spacing.all(0)
