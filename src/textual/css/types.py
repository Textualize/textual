from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


Visibility = Literal["visible", "hidden", "initial", "inherit"]
Display = Literal["block", "none"]
