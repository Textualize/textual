"""
General exception classes.

"""

from __future__ import annotations


class TextualError(Exception):
    """Base class for Textual errors."""


class NoWidget(TextualError):
    """Specified widget was not found."""


class RenderError(TextualError):
    """An object could not be rendered."""


class DuplicateKeyHandlers(TextualError):
    """More than one handler for a single key press.

    For example, if the handlers `key_ctrl_i` and `key_tab` were defined on the same
    widget, then this error would be raised.
    """
