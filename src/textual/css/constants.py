import sys

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final  # pragma: no cover

from ..geometry import Spacing

VALID_VISIBILITY: Final = {"visible", "hidden"}
VALID_DISPLAY: Final = {"block", "none"}
VALID_BORDER: Final = {
    "rounded",
    "solid",
    "double",
    "dashed",
    "heavy",
    "inner",
    "outer",
}
VALID_EDGE: Final = {"", "top", "right", "bottom", "left"}
VALID_LAYOUT: Final = {"dock", "vertical", "grid"}


NULL_SPACING: Final = Spacing(0, 0, 0, 0)
