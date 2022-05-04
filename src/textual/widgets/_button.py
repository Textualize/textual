from __future__ import annotations

from typing import cast

from rich.console import RenderableType
from rich.text import Text

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
        padding: 0 2;
        background: $primary;
        color: $text-primary;
        content-align: center middle;
        border: tall $primary-lighten-3;                
        
        margin: 1 0;
        text-style: bold;
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
        label: RenderableType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)

        self.label = self.css_identifier_styled if label is None else label
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
        return self.label

    async def on_click(self, event: events.Click) -> None:
        event.stop()
        if not self.disabled:
            await self.emit(Button.Pressed(self))

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and not self.disabled:
            await self.emit(Button.Pressed(self))
