"""Provides the base code and implementations of toggle widgets.

In particular it provides `Checkbox`, `RadioButton` and `RadioSet`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rich.console import RenderableType

from textual.binding import Binding, BindingType
from textual.content import Content, ContentText
from textual.events import Click
from textual.geometry import Size
from textual.message import Message
from textual.reactive import reactive
from textual.style import Style
from textual.widgets._static import Static

if TYPE_CHECKING:
    from typing_extensions import Self


class ToggleButton(Static, can_focus=True):
    """Base toggle button widget.

    Warning:
        `ToggleButton` should be considered to be an internal class; it
        exists to serve as the common core of [Checkbox][textual.widgets.Checkbox] and
        [RadioButton][textual.widgets.RadioButton].
    """

    ALLOW_SELECT = False
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space", "toggle_button", "Toggle", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter, space | Toggle the value. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "toggle--button",
        "toggle--label",
    }
    """
    | Class | Description |
    | :- | :- |
    | `toggle--button` | Targets the toggle button itself. |
    | `toggle--label` | Targets the text label of the toggle button. |
    """

    DEFAULT_CSS = """
    ToggleButton {
        width: auto;
        border: tall $border-blurred;
        padding: 0 1;
        background: $surface;
        text-wrap: nowrap;
        text-overflow: ellipsis;

        &.-textual-compact {
            border: none !important;
            padding: 0;
            &:focus {
                border: tall $border;
                background-tint: $foreground 5%;
                & > .toggle--label {
                    color: $block-cursor-foreground;
                    background: $block-cursor-background;
                    text-style: $block-cursor-text-style;
                }
            }
        }

        & > .toggle--button {
            color: $panel-darken-2;
            background: $panel;
        }

        &.-on > .toggle--button {
            color: $text-success;
            background: $panel;
        }

        &:focus {       
            border: tall $border;            
            background-tint: $foreground 5%;     
     
            & > .toggle--label {                         
                color: $block-cursor-foreground;
                background: $block-cursor-background;       
                text-style: $block-cursor-text-style;                
            }
        }
        &:blur:hover {
            & > .toggle--label {
                background: $block-hover-background;
            }
        }
    }
    """

    BUTTON_LEFT: str = "▐"
    """The character used for the left side of the toggle button."""

    BUTTON_INNER: str = "X"
    """The character used for the inside of the button."""

    BUTTON_RIGHT: str = "▌"
    """The character used for the right side of the toggle button."""

    value: reactive[bool] = reactive(False, init=False)
    """The value of the button. `True` for on, `False` for off."""

    compact: reactive[bool] = reactive(False, toggle_class="-textual-compact")
    """Enable compact display?"""

    def __init__(
        self,
        label: ContentText = "",
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        compact: bool = False,
    ) -> None:
        """Initialise the toggle.

        Args:
            label: The label for the toggle.
            value: The initial value of the toggle.
            button_first: Should the button come before the label, or after?
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
            disabled: Whether the button is disabled or not.
            tooltip: RenderableType | None = None,
            compact: Show a compact button.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._button_first = button_first
        # NOTE: Don't send a Changed message in response to the initial set.
        with self.prevent(self.Changed):
            self.value = value
        self._label = self._make_label(label)
        if tooltip is not None:
            self.tooltip = tooltip
        self.compact = compact

    def _make_label(self, label: ContentText) -> Content:
        """Make label content.

        Args:
            label: The source value for the label.

        Returns:
            A `Content` rendering of the label for use in the button.
        """
        label = Content.from_text(label).first_line.rstrip()
        return label

    @property
    def label(self) -> Content:
        """The label associated with the button."""
        return self._label

    @label.setter
    def label(self, label: ContentText) -> None:
        self._label = self._make_label(label)
        self.refresh(layout=True)

    @property
    def _button(self) -> Content:
        """The button, reflecting the current value."""

        # Grab the button style.
        button_style = self.get_visual_style("toggle--button")

        # Building the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style(
            foreground=button_style.background,
            background=self.background_colors[1],
        )

        return Content.assemble(
            (self.BUTTON_LEFT, side_style),
            (self.BUTTON_INNER, button_style),
            (self.BUTTON_RIGHT, side_style),
        )

    def render(self) -> Content:
        """Render the content of the widget.

        Returns:
            The content to render for the widget.
        """
        button = self._button
        label_style = self.get_visual_style("toggle--label")
        label = self._label.pad(1, 1).stylize_before(label_style)

        if self._button_first:
            content = Content.assemble(button, label)
        else:
            content = Content.assemble(label, button)
        return content

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return (
            self._button.get_optimal_width(self.styles, 0)
            + (2 if self._label else 0)
            + self._label.get_optimal_width(self.styles, 0)
        )

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 1

    def toggle(self) -> Self:
        """Toggle the value of the widget.

        Returns:
            The `ToggleButton` instance.
        """
        self.value = not self.value
        return self

    def action_toggle_button(self) -> None:
        """Toggle the value of the widget when called as an action.

        This would normally be used for a keyboard binding.
        """
        self.toggle()

    async def _on_click(self, _: Click) -> None:
        """Toggle the value of the widget when clicked with the mouse."""
        self.toggle()

    class Changed(Message):
        """Posted when the value of the toggle button changes."""

        def __init__(self, toggle_button: ToggleButton, value: bool) -> None:
            """Initialise the message.

            Args:
                toggle_button: The toggle button sending the message.
                value: The value of the toggle button.
            """
            super().__init__()
            self._toggle_button = toggle_button
            """A reference to the toggle button that was changed."""
            self.value = value
            """The value of the toggle button after the change."""

    def watch_value(self) -> None:
        """React to the value being changed.

        When triggered, the CSS class `-on` is applied to the widget if
        `value` has become `True`, or it is removed if it has become
        `False`. Subsequently a related `Changed` event will be posted.
        """
        self.set_class(self.value, "-on")
        self.post_message(self.Changed(self, self.value))
