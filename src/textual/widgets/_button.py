from __future__ import annotations

import sys
from typing import cast

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover

from rich.console import RenderableType
from rich.text import Text, TextType

from .. import events
from ..css._error_tools import friendly_list
from ..message import Message
from ..reactive import Reactive
from ..widget import Widget

ButtonVariant = Literal["default", "success", "warning", "error"]
_VALID_BUTTON_VARIANTS = ButtonVariant.__args__  # type: ignore


class InvalidButtonVariant(Exception):
    pass


class Button(Widget, can_focus=True):
    """A simple clickable button."""

    CSS = """
    Button {
        width: auto;
        height: 3;

        background: $primary;
        color: $text-primary;
        border: tall $primary-lighten-3;

        content-align: center middle;
        margin: 1 0;
        align: center middle;
        text-style: bold;
    }

    Button:hover {
        background: $primary-darken-2;
        color: $text-primary-darken-2;
        border: tall $primary-lighten-1;
    }

    .-dark-mode Button {
        background: $background;
        color: $primary-lighten-2;
        border: tall white $primary-lighten-2;
    }

    .-dark-mode Button:hover {
        background: $surface;
    }

    /* Success variant */
    Button.-success {
        background: $success;
        color: $text-success;
        border: tall $success-lighten-3;
    }

    Button.-success:hover {
        background: $success-darken-1;
        color: $text-success-darken-1;
        border: tall $success-lighten-2;
    }

    .-dark-mode Button.-success {
        background: $success;
        color: $text-success;
        border: tall $success-lighten-3;
    }

    .-dark-mode Button.-success:hover {
        background: $success-darken-1;
        color: $text-success-darken-1;
        border: tall $success-lighten-3;
    }

    /* Warning variant */
    Button.-warning {
        background: $warning;
        color: $text-warning;
        border: tall $warning-lighten-3;
    }

    Button.-warning:hover {
        background: $warning-darken-1;
        color: $text-warning-darken-1;
        border: tall $warning-lighten-3;
    }

    .-dark-mode Button.-warning {
        background: $warning;
        color: $text-warning;
        border: tall $warning-lighten-3;
    }

    .-dark-mode Button.-warning:hover {
        background: $warning-darken-1;
        color: $text-warning-darken-1;
        border: tall $warning-lighten-3;
    }

    /* Error variant */
    Button.-error {
        background: $error;
        color: $text-error;
        border: tall $error-lighten-3;
    }

    Button.-error:hover {
        background: $error-darken-1;
        color: $text-error-darken-1;
        border: tall $error-lighten-3;
    }

    .-dark-mode Button.-error {
        background: $error;
        color: $text-error;
        border: tall $error-lighten-3;
    }

    .-dark-mode Button.-error:hover {
        background: $error-darken-1;
        color: $text-error-darken-1;
        border: tall $error-lighten-3;
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
        variant: ButtonVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Create a Button widget.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            variant (ButtonVariant): The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
        """
        super().__init__(name=name, id=id, classes=classes)

        if label is None:
            label = self.css_identifier_styled

        self.label: Text = label

        self.disabled = disabled
        if disabled:
            self.add_class("-disabled")

        if variant in _VALID_BUTTON_VARIANTS:
            if variant != "default":
                self.add_class(f"-{variant}")

        else:
            raise InvalidButtonVariant(
                f"Valid button variants are {friendly_list(_VALID_BUTTON_VARIANTS)}"
            )

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

    @classmethod
    def success(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating a success Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'success' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="success",
            name=name,
            id=id,
            classes=classes,
        )

    @classmethod
    def warning(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating a warning Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'warning' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="warning",
            name=name,
            id=id,
            classes=classes,
        )

    @classmethod
    def error(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating an error Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'error' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="error",
            name=name,
            id=id,
            classes=classes,
        )
