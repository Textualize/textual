"""Provides a Textual placeholder widget; useful when designing an app's layout."""

from __future__ import annotations

from itertools import cycle

from rich.console import RenderableType
from typing_extensions import Literal

from .. import events
from ..css._error_tools import friendly_list
from ..reactive import Reactive, reactive
from ..widget import Widget

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
    }
    Placeholder.-text {
        padding: 1;
    }

    """

    # Consecutive placeholders get assigned consecutive colors.
    _COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)
    _SIZE_RENDER_TEMPLATE = "[b]{} x {}[/b]"

    variant: Reactive[PlaceholderVariant] = reactive[PlaceholderVariant]("default")

    _renderables: dict[PlaceholderVariant, str]

    @classmethod
    def reset_color_cycle(cls) -> None:
        """Reset the placeholder background color cycle."""
        cls._COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)

    def __init__(
        self,
        label: str | None = None,
        variant: PlaceholderVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Create a Placeholder widget.

        Args:
            label: The label to identify the placeholder.
                If no label is present, uses the placeholder ID instead.
            variant: The variant of the placeholder.
            name: The name of the placeholder. Defaults to None.
            id: The ID of the placeholder in the DOM.
            classes: A space separated string with the CSS classes
                of the placeholder, if any.
        """
        # Create and cache renderables for all the variants.
        self._renderables = {
            "default": label if label else f"#{id}" if id else "Placeholder",
            "size": "",
            "text": "\n\n".join(_LOREM_IPSUM_PLACEHOLDER_TEXT for _ in range(5)),
        }

        super().__init__(name=name, id=id, classes=classes)

        self.styles.background = f"{next(Placeholder._COLORS)} 50%"

        self.variant = self.validate_variant(variant)
        """The current variant of the placeholder."""

        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

    def render(self) -> RenderableType:
        """Render the placeholder.

        Returns:
            The value to render.
        """
        return self._renderables[self.variant]

    def cycle_variant(self) -> None:
        """Get the next variant in the cycle."""
        self.variant = next(self._variants_cycle)

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

    def on_click(self) -> None:
        """Click handler to cycle through the placeholder variants."""
        self.cycle_variant()

    def on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        self._renderables["size"] = self._SIZE_RENDER_TEMPLATE.format(*event.size)
        if self.variant == "size":
            self.refresh()
