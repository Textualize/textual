from __future__ import annotations

from itertools import cycle
from typing import Literal

from rich.pretty import Pretty

from .. import events
from ..css._error_tools import friendly_list
from ..reactive import reactive
from ..widgets import Static

PlaceholderVariant = Literal["default", "state", "size", "css", "text"]
_VALID_PLACEHOLDER_VARIANTS_ORDERED = ["default", "state", "size", "css", "text"]
_VALID_PLACEHOLDER_VARIANTS = set(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
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


class InvalidPlaceholderVariant(Exception):
    pass


class Placeholder(Static, can_focus=True):
    """A simple placeholder widget to use before you build your custom widgets.

    This placeholder has a couple of variants that show different data.
    Clicking the placeholder cycles through the available variants, but a placeholder
    can also be initialised in a specific variant.

    The variants available are:
        default: shows a placeholder with a solid color.
        state: shows the placeholder mouse over and focus state.
        size: shows the size of the placeholder.
        css: shows the CSS rules that apply to the placeholder.
        text: shows some Lorem Ipsum text on the placeholder.
    """

    DEFAULT_CSS = """
    Placeholder {
        content-align: center middle;
    }
    """
    # Consecutive placeholders get assigned consecutive colors.
    COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)

    variant = reactive("default")

    def __init__(
        self,
        variant: PlaceholderVariant = "default",
        *,
        label: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Create a Placeholder widget.

        Args:
            variant (PlaceholderVariant, optional): The variant of the placeholder.
                Defaults to "default".
            label (str | None, optional): The label to identify the placeholder.
                If no label is present, uses the placeholder ID instead. Defaults to None.
            name (str | None, optional): The name of the placeholder. Defaults to None.
            id (str | None, optional): The ID of the placeholder in the DOM.
                Defaults to None.
            classes (str | None, optional): A space separated string with the CSS classes
                of the placeholder, if any. Defaults to None.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._placeholder_label = label if label else f"#{id}" if id else "Placeholder"
        self.color = next(Placeholder.COLORS)
        self.styles.background = f"{self.color} 70%"
        self.variant = self.validate_variant(variant)
        # Set a cycle through the variants with the correct starting point.
        self.variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self.variants_cycle) != self.variant:
            pass

    def on_click(self) -> None:
        """Clicking on the placeholder cycles through the placeholder variants."""
        self.cycle_variant()

    def cycle_variant(self) -> None:
        """Get the next variant in the cycle."""
        self.variant = next(self.variants_cycle)

    def watch_variant(self, old_variant: str, variant: str) -> None:
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
        self.update_on_variant_change(variant)

    def update_on_variant_change(self, variant: str) -> None:
        """Calls the appropriate method to update the render of the placeholder."""
        update_variant_method = getattr(self, f"_update_{variant}_variant", None)
        if update_variant_method is None:
            raise InvalidPlaceholderVariant(
                "Valid placeholder variants are "
                + f"{friendly_list(_VALID_PLACEHOLDER_VARIANTS)}"
            )
        update_variant_method()

    def _update_default_variant(self) -> None:
        """Update the placeholder with its label."""
        self.update(self._placeholder_label)

    def _update_state_variant(self) -> None:
        """Update the placeholder with its focus and mouse over status."""
        data = {"has_focus": self.has_focus, "mouse_over": self.mouse_over}
        self.update(Pretty(data))

    def _update_size_variant(self) -> None:
        """Update the placeholder with the size of the placeholder."""
        width, height = self.size
        size_data = {
            "width": width,
            "height": height,
        }
        self.update(Pretty(size_data))

    def _update_css_variant(self) -> None:
        """Update the placeholder with the CSS rules applied to this placeholder."""
        self.update(self.styles.css)

    def _update_text_variant(self) -> None:
        """Update the placeholder with some Lorem Ipsum text."""
        self.update(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam feugiat ac elit sit amet accumsan. Suspendisse bibendum nec libero quis gravida. Phasellus id eleifend ligula. Nullam imperdiet sem tellus, sed vehicula nisl faucibus sit amet. Praesent iaculis tempor ultricies. Sed lacinia, tellus id rutrum lacinia, sapien sapien congue mauris, sit amet pellentesque quam quam vel nisl. Curabitur vulputate erat pellentesque mauris posuere, non dictum risus mattis."
        )

    def on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        if self.variant == "size":
            self._update_size_variant()

    def watch_has_focus(self, has_focus: bool) -> None:
        """Update the placeholder "state" variant with the new focus state."""
        if self.variant == "state":
            self._update_state_variant()

    def watch_mouse_over(self, mouse_over: bool) -> None:
        """Update the placeholder "state" variant with the new mouse over state."""
        if self.variant == "state":
            self._update_state_variant()

    def validate_variant(self, variant: PlaceholderVariant) -> str:
        """Validate the variant to which the placeholder was set."""
        if variant not in _VALID_PLACEHOLDER_VARIANTS:
            raise InvalidPlaceholderVariant(
                "Valid placeholder variants are "
                + f"{friendly_list(_VALID_PLACEHOLDER_VARIANTS)}"
            )
        return variant
