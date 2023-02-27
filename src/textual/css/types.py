from __future__ import annotations

from typing import Tuple

from typing_extensions import Literal

from ..color import Color

Edge = Literal["top", "right", "bottom", "left"]
DockEdge = Literal["top", "right", "bottom", "left", ""]
EdgeType = Literal[
    "",
    "ascii",
    "none",
    "hidden",
    "blank",
    "round",
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
]
Visibility = Literal["visible", "hidden", "initial", "inherit"]
Display = Literal["block", "none"]
AlignHorizontal = Literal["left", "center", "right"]
AlignVertical = Literal["top", "middle", "bottom"]
ScrollbarGutter = Literal["auto", "stable"]
BoxSizing = Literal["border-box", "content-box"]
Overflow = Literal["scroll", "hidden", "auto"]
EdgeStyle = Tuple[EdgeType, Color]
TextAlign = Literal["left", "start", "center", "right", "end", "justify"]

Specificity3 = Tuple[int, int, int]
Specificity6 = Tuple[int, int, int, int, int, int]
