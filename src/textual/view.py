from __future__ import annotations

from .widget import Widget

import rich.repr


@rich.repr.auto
class View(Widget):
    """A widget for the root of the app."""

    DEFAULT_STYLES = """

    layout: dock
    docks: _default=top;

    """
