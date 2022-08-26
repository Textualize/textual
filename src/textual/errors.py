from __future__ import annotations


class TextualError(Exception):
    """Base class for Textual errors."""


class NoWidget(TextualError):
    """Specified widget was not found."""


class RenderError(TextualError):
    """An object could not be rendered."""
