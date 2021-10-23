from __future__ import annotations

import sys
from typing import Tuple


from rich.style import Style

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


Visibility = Literal["visible", "hidden", "initial", "inherit"]
Display = Literal["block", "none"]
EdgeStyle = Tuple[str, Style]
