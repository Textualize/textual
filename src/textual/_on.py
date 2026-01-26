from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar

from textual.css.model import SelectorSet
from textual.css.parse import parse_selectors
from textual.css.tokenizer import TokenError
from textual.message import Message

if TYPE_CHECKING:
    from textual.widget import Widget

DecoratedType = TypeVar("DecoratedType")


class OnDecoratorError(Exception):
    """Errors related to the `on` decorator.

    Typically raised at import time as an early warning system.
    """


class OnNoWidget(Exception):
    """A selector was applied to an attribute that isn't a widget."""


def on(
    message_type: type[Message],
    selector: str | None = None,
    *,
    control_type: type["Widget"] | None = None,
    **kwargs: str,
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

    The `control_type` parameter can be used to filter by widget class. This is useful
    when a widget subclass inherits message types from its parent but you want to handle
    only events from the specific subclass.

    Example:
        ```python
        class MyButton(Button):
            pass

        class MyApp(App):
            @on(Button.Pressed, control_type=MyButton)
            def handle_my_button_only(self) -> None:
                # Only handles Button.Pressed from MyButton instances
                ...
        ```

    Args:
        message_type: The message type (i.e. the class).
        selector: An optional [selector](/guide/CSS#selectors). If supplied, the handler will only be called if `selector`
            matches the widget from the `control` attribute of the message.
        control_type: An optional widget class. If supplied, the handler will only be called if
            the message's `control` is an instance of this class (or a subclass).
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

    # Validate control_type if specified
    if control_type is not None:
        if message_type.control == Message.control:
            raise OnDecoratorError(
                "The message class must have a 'control' to use control_type with the on decorator"
            )

    def decorator(method: DecoratedType) -> DecoratedType:
        """Store message and selector in function attribute, return callable unaltered."""

        if not hasattr(method, "_textual_on"):
            setattr(method, "_textual_on", [])
        getattr(method, "_textual_on").append((message_type, parsed_selectors, control_type))

        return method

    return decorator
