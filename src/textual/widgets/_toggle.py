"""Provides the base code and implementations of toggle widgets.

In particular it provides `Checkbox`, `RadioButton` and `RadioSet`.
"""

from __future__ import annotations

from typing import ClassVar

from rich.text import Text, TextType

from ..app import RenderResult
from ..binding import Binding, BindingType
from ..message import Message
from ..reactive import reactive
from ._static import Static


class ToggleButton(Static, can_focus=True):
    """Base toggle button widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space", "toggle", "Toggle", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,space | Toggle the value. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "toggle--label",
        "toggle--button-sides",
        "toggle--button-inner",
    }
    """
    | Class | Description |
    | :- | :- |
    | `toggle--label` | Targets the text label of the toggle button. |
    | `toggle--button-sides` | Targets the side characters of the toggle button. |
    | `toggle--button-inner` | Targets the inner character of the toggle button. |
    """

    DEFAULT_CSS = """
    ToggleButton:hover {
        text-style: bold;
        background: $boost;
    }

    ToggleButton:focus {
        color: $text;
        background: $secondary;
    }
    """  # TODO: https://github.com/Textualize/textual/issues/1780

    button_prefix: reactive[TextType] = reactive[TextType]("[")
    """The character for the left side of the toggle button."""

    button_suffix: reactive[TextType] = reactive[TextType]("]")
    """The character for the right side of the toggle button."""

    button_off: reactive[TextType] = reactive[TextType](" ")
    """The character used to signify that the button is off."""

    button_on: reactive[TextType] = reactive[TextType]("X")
    """The character used to signify that the button is on."""

    label: reactive[TextType] = reactive[TextType]("")
    """The label that describes the toggle."""

    value: reactive[bool] = reactive(False)
    """The value of the button. `True` for on, `False` for off."""

    button_first: reactive[bool] = reactive(True)
    """Should the button come before the label?"""

    def __init__(
        self,
        label: TextType,
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialise the toggle.

        Args:
            label: The label for the toggle.
            value: The initial value of the toggle. Defaults to `False`.
            button_first: Should the button come before the label, or after?
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
        """
        # TODO: disabled once
        # https://github.com/Textualize/textual/pull/1785 is in.
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.button_first = button_first
        self.value = value

    @property
    def _button(self) -> Text:
        """The button, reflecting the current value."""
        side_style = self.get_component_rich_style("toggle--button-sides")
        inner_style = self.get_component_rich_style("toggle--button-inner")
        return Text.assemble(
            Text(self.button_prefix, style=side_style),
            Text(self.button_on if self.value else self.button_off, style=inner_style),
            Text(self.button_suffix, style=side_style),
        )

    def render(self) -> RenderResult:
        """Render the content of the widget.

        Returns:
            The content to render for the widget.
        """
        button = self._button
        label = Text(self.label, style=self.get_component_rich_style("toggle--label"))
        spacer = Text(
            " " if self.label else "",
            style=self.get_component_rich_style("toggle--label"),
        )
        return (
            Text.assemble(button, spacer, label)
            if self.button_first
            else Text.assemble(label, spacer, button)
        )

    def toggle(self) -> None:
        """Toggle the value of the widget."""
        self.value = not self.value

    class Selected(Message, bubble=True):
        """Posted when the user selects the button."""

        def __init__(self, sender: ToggleButton) -> None:
            """Initialise the message.

            Args:
                sender: The toggle button sending the message.
            """
            super().__init__(sender)
            self.input = sender
            """A reference to the toggle button that was selected."""

    def action_toggle(self) -> None:
        """Toggle the value of the widget."""
        self.post_message_no_wait(self.Selected(self))
        self.toggle()

    def on_click(self) -> None:
        """Toggle the value of the widget."""
        self.post_message_no_wait(self.Selected(self))
        self.toggle()

    class Changed(Message, bubble=True):
        """Posted when the value of the toggle button."""

        def __init__(self, sender: ToggleButton, value: bool) -> None:
            """Initialise the message.

            Args:
                sender: The toggle button sending the message.
                value: The value of the toggle button.
            """
            super().__init__(sender)
            self.input = sender
            """A reference to the toggle button that was changed."""
            self.value = value
            """The value of the toggle button after the change."""

    def watch_value(self) -> None:
        """React to the value being changed."""
        self.post_message_no_wait(self.Changed(self, self.value))
