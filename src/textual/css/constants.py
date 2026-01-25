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
    "tab",
    "thick",
    "block",
    "vkey",
    "wide",
}
VALID_EDGE: Final = {"top", "right", "bottom", "left", "none"}
VALID_LAYOUT: Final = {"vertical", "horizontal", "grid", "stream"}

VALID_BOX_SIZING: Final = {"border-box", "content-box"}
VALID_OVERFLOW: Final = {"scroll", "hidden", "auto"}
VALID_ALIGN_HORIZONTAL: Final = {"left", "center", "right"}
VALID_ALIGN_VERTICAL: Final = {"top", "middle", "bottom"}
VALID_POSITION: Final = {"relative", "absolute"}
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
    "ansi",
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
    "nocolor",
    "first-of-type",
    "last-of-type",
    "first-child",
    "last-child",
    "odd",
    "even",
    "empty",
}
VALID_OVERLAY: Final = {"none", "screen"}
VALID_CONSTRAIN: Final = {"inflect", "inside", "none"}
VALID_KEYLINE: Final = {"none", "thin", "heavy", "double"}
VALID_HATCH: Final = {"left", "right", "cross", "vertical", "horizontal"}
VALID_TEXT_WRAP: Final = {"wrap", "nowrap"}
VALID_TEXT_OVERFLOW: Final = {"clip", "fold", "ellipsis"}
VALID_EXPAND: Final = {"greedy", "optimal"}
VALID_SCROLLBAR_VISIBILITY: Final = {"visible", "hidden"}
VALID_POINTER: Final = {
    "alias",
    "cell",
    "copy",
    "crosshair",
    "default",
    "e-resize",
    "ew-resize",
    "grab",
    "grabbing",
    "help",
    "move",
    "n-resize",
    "ne-resize",
    "nesw-resize",
    "no-drop",
    "not-allowed",
    "ns-resize",
    "nw-resize",
    "nwse-resize",
    "pointer",
    "progress",
    "s-resize",
    "se-resize",
    "sw-resize",
    "text",
    "vertical-text",
    "w-resize",
    "wait",
    "zoom-in",
    "zoom-out",
}

HATCHES: Final = {
    "left": "╲",
    "right": "╱",
    "cross": "╳",
    "horizontal": "─",
    "vertical": "│",
}
