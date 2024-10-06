from __future__ import annotations

from typing import Tuple

from typing_extensions import Literal

from textual.color import Color

DockEdge = Literal["none", "top", "right", "bottom", "left"]
EdgeType = Literal[
    "",
    "ascii",
    "none",
    "hidden",
    "blank",
    "round",
    "solid",
    "thick",
    "double",
    "dashed",
    "heavy",
    "inner",
    "outer",
    "hkey",
    "vkey",
    "tall",
    "panel",
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
Constrain = Literal["none", "inflect", "inside"]
Overlay = Literal["none", "screen"]

Specificity3 = Tuple[int, int, int]
Specificity6 = Tuple[int, int, int, int, int, int]

CSSLocation = Tuple[str, str]
"""Represents the definition location of a piece of CSS code.

The first element of the tuple is the file path from where the CSS was read.
If the CSS was read from a Python source file, the second element contains the class
variable from where the CSS was read (e.g., "Widget.DEFAULT_CSS"), otherwise it's an
empty string.
"""
