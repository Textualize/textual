"""Provides a Textual placeholder widget; useful when designing an app's layout."""

from __future__ import annotations

from itertools import cycle
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from typing_extensions import Literal, Self

from textual import events

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual._context import NoActiveAppError
from textual.css._error_tools import friendly_list
from textual.reactive import Reactive, reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import App

PlaceholderVariant = Literal["default", "size", "text"]
"""The different variants of placeholder."""

_VALID_PLACEHOLDER_VARIANTS_ORDERED: list[PlaceholderVariant] = [
    "default",
    "size",
    "text",
]
_VALID_PLACEHOLDER_VARIANTS: set[PlaceholderVariant] = set(
    _VALID_PLACEHOLDER_VARIANTS_ORDERED
)
_PLACEHOLDER_BACKGROUND_COLORS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    "#ee9944",
    "#eedd00",
    "#99dd55",
    "#44dd88",
    "#22ccbb",
    "#00bbcc",
    "#0099cc",
    "#3366bb",
    "#663399",
]
_LOREM_IPSUM_PLACEHOLDER_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam feugiat ac elit sit amet accumsan. Suspendisse bibendum nec libero quis gravida. Phasellus id eleifend ligula. Nullam imperdiet sem tellus, sed vehicula nisl faucibus sit amet. Praesent iaculis tempor ultricies. Sed lacinia, tellus id rutrum lacinia, sapien sapien congue mauris, sit amet pellentesque quam quam vel nisl. Curabitur vulputate erat pellentesque mauris posuere, non dictum risus mattis."


class InvalidPlaceholderVariant(Exception):
    """Raised when an invalid Placeholder variant is set."""


class Placeholder(Widget):
    """A simple placeholder widget to use before you build your custom widgets.

    This placeholder has a couple of variants that show different data.
    Clicking the placeholder cycles through the available variants, but a placeholder
    can also be initialised in a specific variant.

    The variants available are:

    | Variant | Placeholder shows                              |
    |---------|------------------------------------------------|
    | default | Identifier label or the ID of the placeholder. |
    | size    | Size of the placeholder.                       |
    | text    | Lorem Ipsum text.                              |
    """

    DEFAULT_CSS = """
    Placeholder {
        content-align: center middle;
        overflow: hidden;
        color: $text;

        &:disabled {
            opacity: 0.7;
        }
    }
    Placeholder.-text {
        padding: 1;
    }
    """

    # Consecutive placeholders get assigned consecutive colors.
    _COLORS: WeakKeyDictionary[App, int] = WeakKeyDictionary()
    _SIZE_RENDER_TEMPLATE = "[b]{} x {}[/b]"

    variant: Reactive[PlaceholderVariant] = reactive[PlaceholderVariant]("default")

    _renderables: dict[PlaceholderVariant, str]

    def __init__(
        self,
        label: str | None = None,
        variant: PlaceholderVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Create a Placeholder widget.

        Args:
            label: The label to identify the placeholder.
                If no label is present, uses the placeholder ID instead.
            variant: The variant of the placeholder.
            name: The name of the placeholder.
            id: The ID of the placeholder in the DOM.
            classes: A space separated string with the CSS classes
                of the placeholder, if any.
            disabled: Whether the placeholder is disabled or not.
        """
        # Create and cache renderables for all the variants.
        self._renderables = {
            "default": label if label else f"#{id}" if id else "Placeholder",
            "size": "",
            "text": "\n\n".join(_LOREM_IPSUM_PLACEHOLDER_TEXT for _ in range(5)),
        }

        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self.variant = self.validate_variant(variant)
        """The current variant of the placeholder."""

        try:
            self._COLORS[self.app] = self._COLORS.setdefault(self.app, -1) + 1
            self._color_offset = self._COLORS[self.app]
        except NoActiveAppError:
            self._color_offset = 0

        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

    async def _on_compose(self, event: events.Compose) -> None:
        """Set the color for this placeholder."""
        color_count = len(_PLACEHOLDER_BACKGROUND_COLORS)
        color = _PLACEHOLDER_BACKGROUND_COLORS[self._color_offset % color_count]
        self.styles.background = f"{color} 50%"

    def render(self) -> RenderResult:
        """Render the placeholder.

        Returns:
            The value to render.
        """
        return self._renderables[self.variant]

    def cycle_variant(self) -> Self:
        """Get the next variant in the cycle.

        Returns:
            The `Placeholder` instance.
        """
        self.variant = next(self._variants_cycle)
        return self

    def watch_variant(
        self, old_variant: PlaceholderVariant, variant: PlaceholderVariant
    ) -> None:
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")

    def validate_variant(self, variant: PlaceholderVariant) -> PlaceholderVariant:
        """Validate the variant to which the placeholder was set."""
        if variant not in _VALID_PLACEHOLDER_VARIANTS:
            raise InvalidPlaceholderVariant(
                "Valid placeholder variants are "
                + f"{friendly_list(_VALID_PLACEHOLDER_VARIANTS)}"
            )
        return variant

    async def _on_click(self, _: events.Click) -> None:
        """Click handler to cycle through the placeholder variants."""
        self.cycle_variant()

    def _on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        self._renderables["size"] = self._SIZE_RENDER_TEMPLATE.format(*event.size)
        if self.variant == "size":
            self.refresh()
