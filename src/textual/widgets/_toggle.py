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
        "toggle--button-off",
        "toggle--button-on",
    }
    """
    | Class | Description |
    | :- | :- |
    | `toggle--label` | Targets the text label of the toggle button. |
    | `toggle--button-sides` | Targets the side characters of the toggle button. |
    | `toggle--button-off` | Targets the inner character of the toggle button when off. |
    | `toggle--button-on` | Targets the inner character of the toggle button when on. |
    """

    DEFAULT_CSS = """
    ToggleButton:hover {
        text-style: bold;
        background: $boost;
    }

    ToggleButton:focus > .toggle--label {
        text-style: underline;
    }

    ToggleButton > .toggle--button-sides {
        color: $panel-lighten-2;
    }

    ToggleButton:focus > .toggle--button-sides {
        color: $panel-lighten-3;
    }

    ToggleButton > .toggle--button-on {
        color: $success;
        background: $panel-lighten-2;
    }

    ToggleButton:focus > .toggle--button-on {
        background: $panel-lighten-3;
    }

    ToggleButton > .toggle--button-off {
        color: $panel;
        background: $panel-lighten-2;
    }

    ToggleButton:focus > .toggle--button-off {
        background: $panel-lighten-3;
    }
    """  # TODO: https://github.com/Textualize/textual/issues/1780

    button_left: reactive[TextType] = reactive[TextType]("▐")
    """The character for the left side of the toggle button."""

    button_inner: reactive[TextType] = reactive[TextType]("✖")
    """The character used to for the inside of the button."""

    button_right: reactive[TextType] = reactive[TextType]("▌")
    """The character for the right side of the toggle button."""

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
        disabled: bool = False,
    ) -> None:
        """Initialise the toggle.

        Args:
            label: The label for the toggle.
            value: The initial value of the toggle. Defaults to `False`.
            button_first: Should the button come before the label, or after?
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
            disabled: Whether the button is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.label = label
        self.button_first = button_first
        self.value = value

    @property
    def _button(self) -> Text:
        """The button, reflecting the current value."""
        side_style = self.get_component_rich_style("toggle--button-sides")
        inner_style = self.get_component_rich_style(
            f"toggle--button-{'on' if self.value else 'off'}"
        )
        return Text.assemble(
            Text(self.button_left, style=side_style),
            Text(self.button_inner, style=inner_style),
            Text(self.button_right, style=side_style),
        )

    def render(self) -> RenderResult:
        """Render the content of the widget.

        Returns:
            The content to render for the widget.
        """
        button = self._button
        label = Text(self.label, style=self.get_component_rich_style("toggle--label"))
        spacer = Text(" " if self.label else "")
        return (
            Text.assemble(button, spacer, label)
            if self.button_first
            else Text.assemble(label, spacer, button)
        )

    def toggle(self) -> None:
        """Toggle the value of the widget."""
        self.value = not self.value

    def action_toggle(self) -> None:
        """Toggle the value of the widget."""
        self.toggle()

    def on_click(self) -> None:
        """Toggle the value of the widget."""
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
        self.set_class(self.value, "-on")
        self.post_message_no_wait(self.Changed(self, self.value))
