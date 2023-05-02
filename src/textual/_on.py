from __future__ import annotations

from typing import Callable, TypeVar

from .css.parse import parse_selectors
from .css.tokenizer import TokenError
from .message import Message

DecoratedType = TypeVar("DecoratedType")


class OnDecoratorError(Exception):
    """Errors related to the `on` decorator.

    Typically raised at import time as an early warning system.

    """


def on(
    message_type: type[Message], selector: str | None = None
) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare method is a message handler.

    Example:
        ```python
        @on(Button.Pressed, "#quit")
        def quit_button(self) -> None:
            self.app.quit()
        ```

    Args:
        message_type: The message type (i.e. the class).
        selector: An optional [selector](/guide/CSS#selectors). If supplied, the handler will only be called if `selector`
            matches the widget from the `control` attribute of the message.
    """

    if selector is not None and not hasattr(message_type, "control"):
        raise OnDecoratorError(
            "The 'selector' argument requires a message class with a 'control' attribute (such as events from controls)."
        )

    if selector is not None:
        try:
            parse_selectors(selector)
        except TokenError as error:
            raise OnDecoratorError(
                f"Unable to parse selector {selector!r}; check for syntax errors"
            ) from None

    def decorator(method: DecoratedType) -> DecoratedType:
        """Store message and selector in function attribute, return callable unaltered."""

        if not hasattr(method, "_textual_on"):
            setattr(method, "_textual_on", [])
        getattr(method, "_textual_on").append((message_type, selector))

        return method

    return decorator
