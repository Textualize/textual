"""Provides a check box widget."""

from __future__ import annotations

from ._toggle import ToggleButton


class Checkbox(ToggleButton):
    """A check box widget that represents a boolean value."""

    class Selected(ToggleButton.Selected):
        """Posted when the user selects the button."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "checkbox"

    class Changed(ToggleButton.Changed):
        """Posted when the value of the checkbox changes."""

        # https://github.com/Textualize/textual/issues/1814
        namespace = "checkbox"
