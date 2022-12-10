from __future__ import annotations

from itertools import cycle

from .. import events
from ..containers import Container
from ..css._error_tools import friendly_list
from ..reactive import Reactive, reactive
from ..widget import Widget, RenderResult
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
_LOREM_IPSUM_PLACEHOLDER_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam feugiat ac elit sit amet accumsan. Suspendisse bibendum nec libero quis gravida. Phasellus id eleifend ligula. Nullam imperdiet sem tellus, sed vehicula nisl faucibus sit amet. Praesent iaculis tempor ultricies. Sed lacinia, tellus id rutrum lacinia, sapien sapien congue mauris, sit amet pellentesque quam quam vel nisl. Curabitur vulputate erat pellentesque mauris posuere, non dictum risus mattis."


class InvalidPlaceholderVariant(Exception):
    pass


class _PlaceholderLabel(Widget):
    def __init__(self, content, classes) -> None:
        super().__init__(classes=classes)
        self._content = content

    def render(self) -> RenderResult:
        return self._content


class Placeholder(Container):
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
        overflow: hidden;
    }

    Placeholder.-text {
        padding: 1;
    }

    _PlaceholderLabel {
        height: auto;
        color: $text;
    }

    Placeholder > _PlaceholderLabel {
        content-align: center middle;
    }

    Placeholder.-default > _PlaceholderLabel.-size,
    Placeholder.-default > _PlaceholderLabel.-text,
    Placeholder.-size    > _PlaceholderLabel.-default,
    Placeholder.-size    > _PlaceholderLabel.-text,
    Placeholder.-text    > _PlaceholderLabel.-default,
    Placeholder.-text    > _PlaceholderLabel.-size {
        display: none;
    }

    Placeholder.-default > _PlaceholderLabel.-default,
    Placeholder.-size    > _PlaceholderLabel.-size,
    Placeholder.-text    > _PlaceholderLabel.-text {
        display: block;
    }
    """
    # Consecutive placeholders get assigned consecutive colors.
    _COLORS = cycle(_PLACEHOLDER_BACKGROUND_COLORS)
    _SIZE_RENDER_TEMPLATE = "[b]{} x {}[/b]"

    variant: Reactive[PlaceholderVariant] = reactive("default")

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
            label (str | None, optional): The label to identify the placeholder.
                If no label is present, uses the placeholder ID instead. Defaults to None.
            variant (PlaceholderVariant, optional): The variant of the placeholder.
                Defaults to "default".
            name (str | None, optional): The name of the placeholder. Defaults to None.
            id (str | None, optional): The ID of the placeholder in the DOM.
                Defaults to None.
            classes (str | None, optional): A space separated string with the CSS classes
                of the placeholder, if any. Defaults to None.
        """
        # Create and cache labels for all the variants.
        self._default_label = _PlaceholderLabel(
            label if label else f"#{id}" if id else "Placeholder",
            "-default",
        )
        self._size_label = _PlaceholderLabel(
            "",
            "-size",
        )
        self._text_label = _PlaceholderLabel(
            "\n\n".join(_LOREM_IPSUM_PLACEHOLDER_TEXT for _ in range(5)),
            "-text",
        )
        super().__init__(
            self._default_label,
            self._size_label,
            self._text_label,
            name=name,
            id=id,
            classes=classes,
        )

        self.styles.background = f"{next(Placeholder._COLORS)} 50%"

        self.variant = self.validate_variant(variant)
        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

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
        self._size_label._content = self._SIZE_RENDER_TEMPLATE.format(*self.size)
        if self.variant == "size":
            self._size_label.refresh(layout=True)
