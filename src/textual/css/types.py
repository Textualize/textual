from __future__ import annotations

import sys
from typing import Tuple

from ..color import Color

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


Edge = Literal["top", "right", "bottom", "left"]
EdgeType = Literal[
    "",
    "none",
    "hidden",
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
EdgeStyle = Tuple[str, Color]
Specificity3 = Tuple[int, int, int]
Specificity4 = Tuple[int, int, int, int]
