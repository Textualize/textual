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


class OnNoWidget(Exception):
    """A selector was applied to an attribute that isn't a widget."""


def on(
    message_type: type[Message], selector: str | None = None, **kwargs: str
) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare that the method is a message handler.

    The decorator accepts an optional CSS selector that will be matched against a widget exposed by
    a `control` property on the message.

    Example:
        ```python
        # Handle the press of buttons with ID "#quit".
        @on(Button.Pressed, "#quit")
        def quit_button(self) -> None:
            self.app.quit()
        ```

    Keyword arguments can be used to match additional selectors for attributes
    listed in [`ALLOW_SELECTOR_MATCH`][textual.message.Message.ALLOW_SELECTOR_MATCH].

    Example:
        ```python
        # Handle the activation of the tab "#home" within the `TabbedContent` "#tabs".
        @on(TabbedContent.TabActivated, "#tabs", pane="#home")
        def switch_to_home(self) -> None:
            self.log("Switching back to the home tab.")
            ...
        ```

    Args:
        message_type: The message type (i.e. the class).
        selector: An optional [selector](/guide/CSS#selectors). If supplied, the handler will only be called if `selector`
            matches the widget from the `control` attribute of the message.
        **kwargs: Additional selectors for other attributes of the message.
    """

    selectors: dict[str, str] = {}
    if selector is not None:
        selectors["control"] = selector
    if kwargs:
        selectors.update(kwargs)

    parsed_selectors: dict[str, tuple[SelectorSet, ...]] = {}
    for attribute, css_selector in selectors.items():
        if attribute == "control":
            if message_type.control == Message.control:
                raise OnDecoratorError(
                    "The message class must have a 'control' to match with the on decorator"
                )
        elif attribute not in message_type.ALLOW_SELECTOR_MATCH:
            raise OnDecoratorError(
                f"The attribute {attribute!r} can't be matched; have you added it to "
                + f"{message_type.__name__}.ALLOW_SELECTOR_MATCH?"
            )
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
