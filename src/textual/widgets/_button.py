from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

import rich.repr
from rich.cells import cell_len
from rich.console import ConsoleRenderable, RenderableType
from rich.text import Text, TextType
from typing_extensions import Literal, Self

from textual import events

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.binding import Binding
from textual.css._error_tools import friendly_list
from textual.geometry import Size
from textual.message import Message
from textual.pad import HorizontalPad
from textual.reactive import reactive
from textual.widget import Widget

ButtonVariant = Literal["default", "primary", "success", "warning", "error"]
"""The names of the valid button variants.

These are the variants that can be used with a [`Button`][textual.widgets.Button].
"""

_VALID_BUTTON_VARIANTS = {"default", "primary", "success", "warning", "error"}


class InvalidButtonVariant(Exception):
    """Exception raised if an invalid button variant is used."""


class Button(Widget, can_focus=True):
    """A simple clickable button.

    Clicking the button will send a [Button.Pressed][textual.widgets.Button.Pressed] message,
    unless the `action` parameter is provided.

    """

    DEFAULT_CSS = """
    Button {
        width: auto;
        min-width: 16;
        height: auto;
        background: $panel;
        color: $text;
        border: none;
        border-top: tall $panel-lighten-2;
        border-bottom: tall $panel-darken-3;
        text-align: center;
        content-align: center middle;
        text-style: bold;


        &:focus {
            text-style: bold reverse;
        }
        &:hover {
            border-top: tall $panel;
            background: $panel-darken-2;
            color: $text;
        }
        &.-active {
            background: $panel;
            border-bottom: tall $panel-lighten-2;
            border-top: tall $panel-darken-2;
            tint: $background 30%;
        }

        &.-primary {
            background: $primary;
            color: $text;
            border-top: tall $primary-lighten-3;
            border-bottom: tall $primary-darken-3;

            &:hover {
                background: $primary-darken-2;
                color: $text;
                border-top: tall $primary;
            }

            &.-active {
                background: $primary;
                border-bottom: tall $primary-lighten-3;
                border-top: tall $primary-darken-3;
            }
        }

        &.-success {
            background: $success;
            color: $text;
            border-top: tall $success-lighten-2;
            border-bottom: tall $success-darken-3;

            &:hover {
                background: $success-darken-2;
                color: $text;
                border-top: tall $success;
            }

            &.-active {
                background: $success;
                border-bottom: tall $success-lighten-2;
                border-top: tall $success-darken-2;
            }
        }

        &.-warning{
            background: $warning;
            color: $text;
            border-top: tall $warning-lighten-2;
            border-bottom: tall $warning-darken-3;

            &:hover {
                background: $warning-darken-2;
                color: $text;
                border-top: tall $warning;
            }

            &.-active {
                background: $warning;
                border-bottom: tall $warning-lighten-2;
                border-top: tall $warning-darken-2;
            }
        }

        &.-error {
            background: $error;
            color: $text;
            border-top: tall $error-lighten-2;
            border-bottom: tall $error-darken-3;

            &:hover {
                background: $error-darken-1;
                color: $text;
                border-top: tall $error;
            }

            &.-active {
                background: $error;
                border-bottom: tall $error-lighten-2;
                border-top: tall $error-darken-2;
            }
        }
    }
    """

    BINDINGS = [Binding("enter", "press", "Press button", show=False)]

    label: reactive[TextType] = reactive[TextType]("")
    """The text label that appears within the button."""

    variant = reactive("default", init=False)
    """The variant name for the button."""

    class Pressed(Message):
        """Event sent when a `Button` is pressed and there is no Button action.

        Can be handled using `on_button_pressed` in a subclass of
        [`Button`][textual.widgets.Button] or in a parent widget in the DOM.
        """

        def __init__(self, button: Button) -> None:
            self.button: Button = button
            """The button that was pressed."""
            super().__init__()

        @property
        def control(self) -> Button:
            """An alias for [Pressed.button][textual.widgets.Button.Pressed.button].

            This will be the same value as [Pressed.button][textual.widgets.Button.Pressed.button].
            """
            return self.button

    def __init__(
        self,
        label: TextType | None = None,
        variant: ButtonVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        action: str | None = None,
    ):
        """Create a Button widget.

        Args:
            label: The text that appears within the button.
            variant: The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            tooltip: Optional tooltip.
            action: Optional action to run when clicked.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        if label is None:
            label = self.css_identifier_styled

        self.label = label
        self.variant = variant
        self.action = action
        self.active_effect_duration = 0.2
        """Amount of time in seconds the button 'press' animation lasts."""

        if tooltip is not None:
            self.tooltip = tooltip

    def get_content_width(self, container: Size, viewport: Size) -> int:
        try:
            return max([cell_len(line) for line in self.label.plain.splitlines()]) + 2
        except ValueError:
            # Empty string label
            return 2

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()
        yield "variant", self.variant, "default"

    def validate_variant(self, variant: str) -> str:
        if variant not in _VALID_BUTTON_VARIANTS:
            raise InvalidButtonVariant(
                f"Valid button variants are {friendly_list(_VALID_BUTTON_VARIANTS)}"
            )
        return variant

    def watch_variant(self, old_variant: str, variant: str):
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")

    def validate_label(self, label: TextType) -> Text:
        """Parse markup for self.label"""
        if isinstance(label, str):
            return Text.from_markup(label)
        return label

    def render(self) -> RenderResult:
        assert isinstance(self.label, Text)
        label = self.label.copy()
        label.stylize_before(self.rich_style)
        return HorizontalPad(
            label,
            1,
            1,
            self.rich_style,
            self._get_rich_justify() or "center",
        )

    def post_render(self, renderable: RenderableType) -> ConsoleRenderable:
        return cast(ConsoleRenderable, renderable)

    async def _on_click(self, event: events.Click) -> None:
        event.stop()
        if not self.has_class("-active"):
            self.press()

    def press(self) -> Self:
        """Animate the button and send the [Pressed][textual.widgets.Button.Pressed] message.

        Can be used to simulate the button being pressed by a user.

        Returns:
            The button instance.
        """
        if self.disabled or not self.display:
            return self
        # Manage the "active" effect:
        self._start_active_affect()
        # ...and let other components know that we've just been clicked:
        if self.action is None:
            self.post_message(Button.Pressed(self))
        else:
            self.call_later(
                self.app.run_action, self.action, default_namespace=self._parent
            )
        return self

    def _start_active_affect(self) -> None:
        """Start a small animation to show the button was clicked."""
        if self.active_effect_duration > 0:
            self.add_class("-active")
            self.set_timer(
                self.active_effect_duration, partial(self.remove_class, "-active")
            )

    def action_press(self) -> None:
        """Activate a press of the button."""
        if not self.has_class("-active"):
            self.press()

    @classmethod
    def success(
        cls,
        label: TextType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Button:
        """Utility constructor for creating a success Button variant.

        Args:
            label: The text that appears within the button.
            disabled: Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.

        Returns:
            A [`Button`][textual.widgets.Button] widget of the 'success'
                [variant][textual.widgets.button.ButtonVariant].
        """
        return Button(
            label=label,
            variant="success",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @classmethod
    def warning(
        cls,
        label: TextType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Button:
        """Utility constructor for creating a warning Button variant.

        Args:
            label: The text that appears within the button.
            disabled: Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.

        Returns:
            A [`Button`][textual.widgets.Button] widget of the 'warning'
                [variant][textual.widgets.button.ButtonVariant].
        """
        return Button(
            label=label,
            variant="warning",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @classmethod
    def error(
        cls,
        label: TextType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Button:
        """Utility constructor for creating an error Button variant.

        Args:
            label: The text that appears within the button.
            disabled: Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.

        Returns:
            A [`Button`][textual.widgets.Button] widget of the 'error'
                [variant][textual.widgets.button.ButtonVariant].
        """
        return Button(
            label=label,
            variant="error",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
