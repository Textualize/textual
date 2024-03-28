from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Final

VALID_VISIBILITY: Final = {"visible", "hidden"}
VALID_DISPLAY: Final = {"block", "none"}
VALID_BORDER: Final = {
    "ascii",
    "blank",
    "dashed",
    "double",
    "heavy",
    "hidden",
    "hkey",
    "inner",
    "none",
    "outer",
    "panel",
    "round",
    "solid",
    "tall",
    "thick",
    "vkey",
    "wide",
}
VALID_EDGE: Final = {"top", "right", "bottom", "left"}
VALID_LAYOUT: Final = {"vertical", "horizontal", "grid"}

VALID_BOX_SIZING: Final = {"border-box", "content-box"}
VALID_OVERFLOW: Final = {"scroll", "hidden", "auto"}
VALID_ALIGN_HORIZONTAL: Final = {"left", "center", "right"}
VALID_ALIGN_VERTICAL: Final = {"top", "middle", "bottom"}
VALID_TEXT_ALIGN: Final = {
    "start",
    "end",
    "left",
    "right",
    "center",
    "justify",
}
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
VALID_PSEUDO_CLASSES: Final = {
    "blur",
    "can-focus",
    "dark",
    "disabled",
    "enabled",
    "focus-within",
    "focus",
    "hover",
    "inline",
    "light",
}
VALID_OVERLAY: Final = {"none", "screen"}
VALID_CONSTRAIN: Final = {"x", "y", "both", "inflect", "none"}
VALID_KEYLINE: Final = {"none", "thin", "heavy", "double"}
