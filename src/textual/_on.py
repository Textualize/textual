from __future__ import annotations

from typing import Callable, TypeVar

from .css.parse import parse_selectors
from .css.tokenizer import TokenError
from .message import Message

DecoratedType = TypeVar("DecoratedType")


class OnDecoratorSelectorError(Exception):
    """The selector in the 'on' decorator failed to parse."""


def on(
    message: type[Message], selector: str | None = None
) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare method is a message handler.

    Args:
        message: The message type (i.e. the class).
        selector: An optional selector. If supplied, the handler will only be called if `selector`
            matches the sender of the message.
    """

    if selector is not None:
        try:
            parse_selectors(selector)
        except TokenError as error:
            raise OnDecoratorSelectorError(
                f"Unable to parse selector {selector!r}; check for syntax errors"
            ) from None

    def decorator(method: DecoratedType) -> DecoratedType:
        if not hasattr(method, "_textual_on"):
            setattr(method, "_textual_on", [])
        getattr(method, "_textual_on").append((message, selector))

        return method

    return decorator


if __name__ == "__main__":
    from textual.app import App, ComposeResult
    from textual.widgets import Button

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield Button("OK", id="ok")
            yield Button("Cancel", id="cancel")

        @on(Button.Pressed, "#ok")
        def ok_pressed(self):
            self.app.bell()

        @on(Button.Pressed, "#cancel")
        def cancel_pressed(self):
            self.app.exit()

    app = TestApp()
    app.run()
