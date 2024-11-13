from __future__ import annotations

from textual.widgets import Static


class Tooltip(Static, inherit_css=False):
    DEFAULT_CSS = """
    Tooltip {
        layer: _tooltips;
        margin: 1 0;
        padding: 1 2;
        background: $panel;
        width: auto;
        height: auto;
        constrain: inside inflect;
        max-width: 40;
        display: none;
        offset-x: -50%;
    }
    """
    DEFAULT_CLASSES = "-textual-system"
