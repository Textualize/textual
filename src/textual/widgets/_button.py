from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

import rich.repr
from rich.cells import cell_len
from rich.console import ConsoleRenderable, RenderableType
from typing_extensions import Literal, Self

from textual import events

if TYPE_CHECKING:
    from textual.app import RenderResult

from rich.style import Style

from textual.binding import Binding
from textual.content import Content, ContentText
from textual.css._error_tools import friendly_list
from textual.geometry import Size
from textual.message import Message
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

    ALLOW_SELECT = False

    DEFAULT_CSS = """
    Button {
        width: auto;
        min-width: 16;
        height:auto;
        line-pad: 1;
        text-align: center;
        content-align: center middle;
        

        &.-style-flat {
            text-style: bold;
            color: auto 90%;
            background: $surface;
            border: block $surface;
            &:hover {
                background: $primary;
                border: block $primary;
            }
            &:focus {
                text-style: $button-focus-text-style;
            }
            &.-active {
                background: $surface;
                border: block $surface;
                tint: $background 30%;
            }
            &:disabled {
                color: auto 50%;
            }

            &.-primary {
                background: $primary-muted;
                border: block $primary-muted;
                color: $text-primary;
                &:hover {
                    color: $text;
                    background: $primary;
                    border: block $primary;
                }
            }
            &.-success {
                background: $success-muted;
                border: block $success-muted;
                color: $text-success;
                &:hover {
                    color: $text;
                    background: $success;
                    border: block $success;
                }
            }
            &.-warning {
                background: $warning-muted;
                border: block $warning-muted;
                color: $text-warning;
                &:hover {
                    color: $text;
                    background: $warning;
                    border: block $warning;
                }
            }
            &.-error {
                background: $error-muted;
                border: block $error-muted;
                color: $text-error;
                &:hover {
                    color: $text;
                    background: $error;
                    border: block $error;
                }
            }
        }
        &.-style-default {
            text-style: bold;
            color: $button-foreground;
            background: $surface;
            border: none;
            border-top: tall $surface-lighten-1;
            border-bottom: tall $surface-darken-1;
            

            &.-textual-compact {
                border: none !important;
            }

            &:disabled {
                text-opacity: 0.6;
            }

            &:focus {
                text-style: $button-focus-text-style;
                background-tint: $foreground 5%;
            }
            &:hover {
                border-top: tall $surface;
                background: $surface-darken-1;
            }
    
            &.-active {
                background: $surface;
                border-bottom: tall $surface-lighten-1;
                border-top: tall $surface-darken-1;
                tint: $background 30%;
            }

            &.-primary {
                color: $button-color-foreground;
                background: $primary;
                border-top: tall $primary-lighten-3;
                border-bottom: tall $primary-darken-3;

                &:hover {
                    background: $primary-darken-2;
                    border-top: tall $primary;
                }

                &.-active {
                    background: $primary;
                    border-bottom: tall $primary-lighten-3;
                    border-top: tall $primary-darken-3;
                }
            }

            &.-success {
                color: $button-color-foreground;
                background: $success;
                border-top: tall $success-lighten-2;
                border-bottom: tall $success-darken-3;

                &:hover {
                    background: $success-darken-2;
                    border-top: tall $success;
                }

                &.-active {
                    background: $success;
                    border-bottom: tall $success-lighten-2;
                    border-top: tall $success-darken-2;
                }
            }

            &.-warning{
                color: $button-color-foreground;
                background: $warning;
                border-top: tall $warning-lighten-2;
                border-bottom: tall $warning-darken-3;

                &:hover {
                    background: $warning-darken-2;
                    border-top: tall $warning;
                }

                &.-active {
                    background: $warning;
                    border-bottom: tall $warning-lighten-2;
                    border-top: tall $warning-darken-2;
                }
            }

            &.-error {
                color: $button-color-foreground;
                background: $error;
                border-top: tall $error-lighten-2;
                border-bottom: tall $error-darken-3;

                &:hover {
                    background: $error-darken-1;
                    border-top: tall $error;
                }

                &.-active {
                    background: $error;
                    border-bottom: tall $error-lighten-2;
                    border-top: tall $error-darken-2;
                }
            }
        }
    }
    """

    BINDINGS = [Binding("enter", "press", "Press button", show=False)]

    label: reactive[ContentText] = reactive[ContentText](Content.empty())
    """The text label that appears within the button."""

    variant = reactive("default", init=False)
    """The variant name for the button."""

    compact = reactive(False, toggle_class="-textual-compact")
    """Make the button compact (without borders)."""

    flat = reactive(False)
    """Enable alternative flat button style."""

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
        label: ContentText | None = None,
        variant: ButtonVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        action: str | None = None,
        compact: bool = False,
        flat: bool = False,
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
            compact: Enable compact button style.
            flat: Enable alternative flat look buttons.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        if label is None:
            label = self.css_identifier_styled

        self.variant = variant
        self.flat = flat
        self.compact = compact
        self.set_reactive(Button.label, Content.from_text(label))

        self.action = action
        self.active_effect_duration = 0.2
        """Amount of time in seconds the button 'press' animation lasts."""

        if tooltip is not None:
            self.tooltip = tooltip

    def get_content_width(self, container: Size, viewport: Size) -> int:
        assert isinstance(self.label, Content)
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

    def watch_flat(self, flat: bool) -> None:
        self.set_class(flat, "-style-flat")
        self.set_class(not flat, "-style-default")

    def validate_label(self, label: ContentText) -> Content:
        """Parse markup for self.label"""
        return Content.from_text(label)

    def render(self) -> RenderResult:
        assert isinstance(self.label, Content)
        return self.label

    def post_render(
        self, renderable: RenderableType, base_style: Style
    ) -> ConsoleRenderable:
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
        label: ContentText | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        flat: bool = False,
    ) -> Button:
        """Utility constructor for creating a success Button variant.

        Args:
            label: The text that appears within the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            flat: Enable alternative flat look buttons.

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
            flat=flat,
        )

    @classmethod
    def warning(
        cls,
        label: ContentText | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        flat: bool = False,
    ) -> Button:
        """Utility constructor for creating a warning Button variant.

        Args:
            label: The text that appears within the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            flat: Enable alternative flat look buttons.

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
            flat=flat,
        )

    @classmethod
    def error(
        cls,
        label: ContentText | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        flat: bool = False,
    ) -> Button:
        """Utility constructor for creating an error Button variant.

        Args:
            label: The text that appears within the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
            flat: Enable alternative flat look buttons.

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
            flat=flat,
        )
