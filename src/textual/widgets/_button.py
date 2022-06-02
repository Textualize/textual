from __future__ import annotations

from typing import cast

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text, TextType

from .. import events
from ..message import Message
from ..reactive import Reactive
from ..widget import Widget


class Button(Widget, can_focus=True):
    """A simple clickable button."""

    CSS = """


    Button {
        width: auto;
        height: 3;
        background: $primary;
        color: $text-primary;
        content-align: center middle;
        border: tall $primary-lighten-3;
        
        margin: 1 0;
        align: center middle;
        text-style: bold;
    }

    .-dark-mode Button {
        border: tall white $primary-lighten-2;
        color: $primary-lighten-2;
        background: $background;
    }

    .-dark-mode Button:hover {
        background: $surface;
    }


    Button:hover {
        background:$primary-darken-2;
        color: $text-primary-darken-2;
        border: tall $primary-lighten-1;
    }

    App.-show-focus Button:focus {
        tint: $accent 20%;
    }

    """

    class Pressed(Message, bubble=True):
        @property
        def button(self) -> Button:
            return cast(Button, self.sender)

    def __init__(
        self,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)

        if label is None:
            label = self.css_identifier_styled

        self.label: Text = label

        self.disabled = disabled
        if disabled:
            self.add_class("-disabled")

    label: Reactive[RenderableType] = Reactive("")

    def validate_label(self, label: RenderableType) -> RenderableType:
        """Parse markup for self.label"""
        if isinstance(label, str):
            return Text.from_markup(label)
        return label

    def render(self) -> RenderableType:
        label = self.label.copy()
        label.stylize(self.text_style)
        return label

    async def on_click(self, event: events.Click) -> None:
        event.stop()
        if not self.disabled:
            await self.emit(Button.Pressed(self))

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and not self.disabled:
            await self.emit(Button.Pressed(self))
