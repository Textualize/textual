from __future__ import annotations

import sys
from typing import Tuple


from rich.style import Style

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


Edge = Literal["top", "right", "bottom", "left"]
Visibility = Literal["visible", "hidden", "initial", "inherit"]
Display = Literal["block", "none"]
EdgeStyle = Tuple[str, Style]
Specificity3 = Tuple[int, int, int]
Specificity4 = Tuple[int, int, int, int]
