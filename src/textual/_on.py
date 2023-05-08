from __future__ import annotations

from typing import Callable, TypeVar

from .css.model import SelectorSet
from .css.parse import parse_selectors
from .css.tokenizer import TokenError
from .message import Message

DecoratedType = TypeVar("DecoratedType")


class OnDecoratorError(Exception):
    """Errors related to the `on` decorator.

    Typically raised at import time as an early warning system.
    """


def on(
    message_type: type[Message], selector: str | None = None, **kwargs: str
) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare that method is a message handler.

    The decorator can take a CSS selector that is applied to the attribute `control`
    of the message.

    Example:
        ```python
        # Handle the press of buttons with ID "#quit".
        @on(Button.Pressed, "#quit")
        def quit_button(self) -> None:
            self.app.quit()
        ```

    Additionally, arbitrary keyword arguments can be used to provide further selectors
    for arbitrary attributes of the messages passed in.

    Example:
        ```python
        # Handle the activation of the tab "#home" within the `TabbedContent` "#tabs".
        @on(TabbedContent.TabActivated, "#tabs", tab="#home")
        def switch_to_home(self) -> None:
            self.log("Switching back to the home tab.")
            ...
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

    selectors: dict[str, str] = {}
    if selector is not None:
        selectors["control"] = selector
    if kwargs:
        selectors.update(kwargs)

    parsed_selectors: dict[str, tuple[SelectorSet, ...]] = {}
    for attribute, css_selector in selectors.items():
        try:
            parsed_selectors[attribute] = parse_selectors(css_selector)
        except TokenError:
            raise OnDecoratorError(
                f"Unable to parse selector {css_selector!r} for {attribute}; check for syntax errors"
            ) from None

    def decorator(method: DecoratedType) -> DecoratedType:
        """Store message and selector in function attribute, return callable unaltered."""

        if not hasattr(method, "_textual_on"):
            setattr(method, "_textual_on", [])
        getattr(method, "_textual_on").append((message_type, parsed_selectors))

        return method

    return decorator
