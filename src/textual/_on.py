from __future__ import annotations

from typing import Callable, TypeVar

from .message import Message

DecoratedType = TypeVar("DecoratedType")


def on(
    message: type[Message], selector: str | None = None
) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare method is a message handler.

    Args:
        message: The message type (i.e. the class).
        selector: An optional selector to match against.
    """

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
        def _(self):
            self.app.bell()

    app = TestApp()
    app.run()
