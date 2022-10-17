from __future__ import annotations


class TextualError(Exception):
    """Base class for Textual errors."""


class NoWidget(TextualError):
    """Specified widget was not found."""


class RenderError(TextualError):
    """An object could not be rendered."""


class DuplicateKeyHandlers(TextualError):
    """More than one handler for a single key press. E.g. key_ctrl_i and key_tab handlers both found on one object."""
