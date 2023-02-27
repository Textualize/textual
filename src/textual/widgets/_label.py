"""Provides a simple Label widget."""

from ._static import Static


class Label(Static):
    """A simple label widget for displaying text-oriented renderables."""

    DEFAULT_CSS = """
    Label {
        width: auto;
        height: auto;
    }
    """
