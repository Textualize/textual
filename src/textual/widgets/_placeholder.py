from __future__ import annotations

from itertools import cycle

from .. import events
from ..app import ComposeResult
from ..css._error_tools import friendly_list
from ..reactive import Reactive, reactive
from ..widgets import Static
from .._typing import Literal

PlaceholderVariant = Literal["default", "size", "text"]
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


class InvalidPlaceholderVariant(Exception):
    pass


class _PlaceholderLabel(Static):
    pass


class Placeholder(Static):
    """A simple placeholder widget to use before you build your custom widgets.

    This placeholder has a couple of variants that show different data.
    Clicking the placeholder cycles through the available variants, but a placeholder
    can also be initialised in a specific variant.

    The variants available are:
        default: shows an identifier label or the ID of the placeholder.
        size: shows the size of the placeholder.
        text: shows some Lorem Ipsum text on the placeholder.
    """

    DEFAULT_CSS = """
    Placeholder {
        align: center middle;
        overflow-y: auto;
    }

    Placeholder.-text {
        padding: 1;
    }

    Placeholder > _PlaceholderLabel {
        content-align: center middle;
    }
    """
    # Consecutive placeholders get assigned consecutive colors.
    COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)

    variant: Reactive[PlaceholderVariant] = reactive("default")

    @classmethod
    def reset_color_cycle(cls) -> None:
        """Reset the placeholder background color cycle."""
        cls.COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)

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
        self._placeholder_text = label if label else f"#{id}" if id else "Placeholder"
        self._placeholder_label = _PlaceholderLabel()
        self.styles.background = f"{next(Placeholder.COLORS)} 70%"
        self.variant = self.validate_variant(variant)
        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

    def compose(self) -> ComposeResult:
        yield self._placeholder_label

    def on_click(self) -> None:
        """Click handler to cycle through the placeholder variants."""
        self.cycle_variant()

    def cycle_variant(self) -> None:
        """Get the next variant in the cycle."""
        self.variant = next(self._variants_cycle)

    def watch_variant(
        self, old_variant: PlaceholderVariant, variant: PlaceholderVariant
    ) -> None:
        self.validate_variant(variant)
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
        self.call_variant_update()

    def call_variant_update(self) -> None:
        """Calls the appropriate method to update the render of the placeholder."""
        update_variant_method = getattr(self, f"_update_{self.variant}_variant")
        assert update_variant_method is not None
        update_variant_method()

    def _update_default_variant(self) -> None:
        """Update the placeholder with its label."""
        self._placeholder_label.update(self._placeholder_text)

    def _update_size_variant(self) -> None:
        """Update the placeholder with the size of the placeholder."""
        width, height = self.size
        self._placeholder_label.update(f"[b]{width} x {height}[/b]")

    def _update_text_variant(self) -> None:
        """Update the placeholder with some Lorem Ipsum text."""
        self._placeholder_label.update(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam feugiat ac elit sit amet accumsan. Suspendisse bibendum nec libero quis gravida. Phasellus id eleifend ligula. Nullam imperdiet sem tellus, sed vehicula nisl faucibus sit amet. Praesent iaculis tempor ultricies. Sed lacinia, tellus id rutrum lacinia, sapien sapien congue mauris, sit amet pellentesque quam quam vel nisl. Curabitur vulputate erat pellentesque mauris posuere, non dictum risus mattis."
        )

    def on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        if self.variant == "size":
            self._update_size_variant()

    def validate_variant(self, variant: PlaceholderVariant) -> PlaceholderVariant:
        """Validate the variant to which the placeholder was set."""
        if variant not in _VALID_PLACEHOLDER_VARIANTS:
            raise InvalidPlaceholderVariant(
                "Valid placeholder variants are "
                + f"{friendly_list(_VALID_PLACEHOLDER_VARIANTS)}"
            )
        return variant
