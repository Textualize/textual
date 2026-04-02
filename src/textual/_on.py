from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from textual.css.model import SelectorSet
from textual.css.parse import parse_selectors
from textual.css.tokenizer import TokenError
from textual.message import Message

if TYPE_CHECKING:
    pass

DecoratedType = TypeVar("DecoratedType")


class OnDecoratorError(Exception):
    """Errors related to the `on` decorator.

    Typically raised at import time as an early warning system.
    """


class OnNoWidget(Exception):
    """A selector was applied to an attribute that isn't a widget."""


class _NamespacedMessage:
    """Wrapper returned when an inherited message class is accessed via a widget subclass.

    This allows ``@on(MyButton.Pressed)`` to implicitly constrain the handler
    to fire only when the event's control is an instance of ``MyButton``, rather
    than matching *any* ``Button.Pressed`` event (which is the same class object).
    """

    def __init__(self, message_class: type[Message], widget_class: type) -> None:
        self._message_class = message_class
        self._widget_class = widget_class

    def __getattr__(self, name: str) -> Any:
        return getattr(self._message_class, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Message:
        return self._message_class(*args, **kwargs)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _NamespacedMessage):
            return (
                self._message_class is other._message_class
                and self._widget_class is other._widget_class
            )
        return self._message_class is other

    def __hash__(self) -> int:
        return hash(self._message_class)

    def __repr__(self) -> str:
        return f"<NamespacedMessage {self._widget_class.__name__}.{self._message_class.__name__}>"


class _MessageClassDescriptor:
    """Descriptor installed on a widget subclass for an inherited message class.

    When ``MyButton.Pressed`` is accessed (where ``Pressed`` is inherited from
    ``Button`` and not overridden), this descriptor returns a
    :class:`_NamespacedMessage` that carries ``MyButton`` as the implicit
    widget-type constraint for the ``@on`` decorator.
    """

    def __init__(self, message_class: type[Message], widget_class: type) -> None:
        self._message_class = message_class
        self._widget_class = widget_class

    def __get__(
        self, obj: object, objtype: type | None = None
    ) -> _NamespacedMessage:
        # If accessed via a further subclass, use that subclass as the namespace.
        namespace = objtype if (objtype is not None) else self._widget_class
        return _NamespacedMessage(self._message_class, namespace)

    def __set__(self, obj: object, value: object) -> None:
        raise AttributeError("Cannot set a message class attribute")

    def __repr__(self) -> str:
        return (
            f"<_MessageClassDescriptor "
            f"{self._widget_class.__name__}.{self._message_class.__name__}>"
        )


def on(
    message_type: type[Message] | _NamespacedMessage,
    selector: str | None = None,
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

    Args:
        message_type: The message type (i.e. the class).
        selector: An optional [selector](/guide/CSS#selectors). If supplied, the handler will only be called if `selector`
            matches the widget from the `control` attribute of the message.
        **kwargs: Additional selectors for other attributes of the message.
    """

    # If the message type was accessed via a widget subclass (e.g. MyButton.Pressed
    # where MyButton inherits Pressed from Button), capture the widget class so the
    # handler will only fire when the event's control is an instance of that subclass.
    namespace_widget: type | None = None
    if isinstance(message_type, _NamespacedMessage):
        namespace_widget = message_type._widget_class
        message_type = message_type._message_class

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
        getattr(method, "_textual_on").append(
            (message_type, parsed_selectors, namespace_widget)
        )

        return method

    return decorator
