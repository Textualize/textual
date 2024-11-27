from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from itertools import islice
from marshal import loads
from typing import TYPE_CHECKING, Any, Iterable, Protocol, cast

import rich.repr
from rich.console import Console, ConsoleOptions, RenderableType
from rich.measure import Measurement
from rich.protocol import is_renderable, rich_cast
from rich.segment import Segment
from rich.style import Style as RichStyle
from rich.terminal_theme import TerminalTheme
from rich.text import Text

from textual._context import active_app
from textual.color import TRANSPARENT, Color
from textual.css.styles import StylesBase
from textual.css.types import AlignHorizontal, AlignVertical
from textual.geometry import Spacing
from textual.render import measure
from textual.strip import Strip

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from textual.widget import Widget

_NULL_RICH_STYLE = RichStyle()


def is_visual(obj: object) -> bool:
    """Check if the given object is a Visual or supports the Visual protocol."""
    return isinstance(obj, Visual) or hasattr(obj, "textualize")


# Note: not runtime checkable currently, as I've found that to be slow
class SupportsVisual(Protocol):
    """An object that supports the textualize protocol."""

    def visualize(self, widget: Widget, obj: object) -> Visual | None:
        """Convert the result of a Widget.render() call in to a Visual, using the Visual protocol.

        Args:
            widget: The widget that generated the render.
            obj: The result of the the render.

        Returns:
            A Visual instance, or `None` if it wasn't possible.

        """


class VisualError(Exception):
    """An error with the visual protocol."""


VisualType: TypeAlias = "RenderableType | SupportsVisual | Visual"


def visualize(widget: Widget, obj: object) -> Visual:
    """Get a visual instance from an object.

    If the object does not support the Visual protocol and is a Rich renderable, it
    will be wrapped in a [RichVisual][textual.visual.RichVisual].

    Args:
        obj: An object.

    Returns:
        A Visual instance to render the object, or `None` if there is no associated visual.
    """
    if isinstance(obj, Visual):
        # Already a visual
        return obj
    # The visualize method should return a Visual if present.
    visualize = getattr(obj, "visualize", None)
    if visualize is None:
        # Doesn't expose the textualize protocol
        if is_renderable(obj):
            # If it is a string, render it to Text
            if isinstance(obj, str):
                obj = widget.render_str(obj)

            # If its is a Rich renderable, wrap it with a RichVisual
            return RichVisual(widget, rich_cast(obj))
        else:
            # We don't know how to make a visual from this object
            raise VisualError(
                f"unable to display {obj.__class__.__name__!r} type; must be a str, Rich renderable, or Textual Visual object"
            )
    # Call the textualize method to create a visual
    visual = visualize()
    if not isinstance(visual, Visual) and is_renderable(visual):
        return RichVisual(widget, visual)
    return visual


@rich.repr.auto
@dataclass(frozen=True)
class Style:
    """Represents a style in the Visual interface (color and other attributes)."""

    background: Color = TRANSPARENT
    foreground: Color = TRANSPARENT
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    link: str | None = None
    _meta: bytes | None = None
    auto_color: bool = False

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.background
        yield None, self.foreground
        yield "bold", self.bold, None
        yield "dim", self.dim, None
        yield "italic", self.italic, None
        yield "underline", self.underline, None
        yield "strike", self.strike, None

    @lru_cache(maxsize=1024)
    def __add__(self, other: object) -> Style:
        if not isinstance(other, Style):
            return NotImplemented
        new_style = Style(
            self.background + other.background,
            self.foreground if other.foreground.is_transparent else other.foreground,
            self.bold if other.bold is None else other.bold,
            self.dim if other.dim is None else other.dim,
            self.italic if other.italic is None else other.italic,
            self.underline if other.underline is None else other.underline,
            self.strike if other.strike is None else other.strike,
            self.link if other.link is None else other.link,
            self._meta if other._meta is None else other._meta,
        )
        return new_style

    @classmethod
    def from_rich_style(
        cls, rich_style: RichStyle, theme: TerminalTheme | None = None
    ) -> Style:
        """Build a Style from a (Rich) Style.

        Args:
            rich_style: A Rich Style object.
            theme: Optional Rich [terminal theme][rich.terminal_theme.TerminalTheme].

        Returns:
            New Style.
        """
        return Style(
            Color.from_rich_color(rich_style.bgcolor, theme),
            Color.from_rich_color(rich_style.color, theme),
            bold=rich_style.bold,
            dim=rich_style.dim,
            italic=rich_style.italic,
            underline=rich_style.underline,
            strike=rich_style.strike,
        )

    @classmethod
    def from_styles(cls, styles: StylesBase) -> Style:
        """Create a Visual Style from a Textual styles object.

        Args:
            styles: A Styles object, such as `my_widget.styles`.

        """
        text_style = styles.text_style
        return Style(
            styles.background,
            (
                Color(0, 0, 0, styles.color.a, auto=True)
                if styles.auto_color
                else styles.color
            ),
            bold=text_style.bold,
            dim=text_style.italic,
            italic=text_style.italic,
            underline=text_style.underline,
            strike=text_style.strike,
            auto_color=styles.auto_color,
        )

    @cached_property
    def rich_style(self) -> RichStyle:
        """Convert this Styles in to a Rich style.

        Returns:
            A Rich style object.
        """
        return RichStyle(
            color=(self.background + self.foreground).rich_color,
            bgcolor=self.background.rich_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            strike=self.strike,
            link=self.link,
            meta=self.meta,
        )

    @cached_property
    def without_color(self) -> Style:
        return Style(
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            strike=self.strike,
            link=self.link,
            _meta=self._meta,
        )

    @classmethod
    def combine(cls, styles: Iterable[Style]) -> Style:
        """Add a number of styles and get the result."""
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @property
    def meta(self) -> dict[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else cast(dict[str, Any], loads(self._meta))


class Visual(ABC):
    """A Textual 'visual' object.

    Analogous to a Rich renderable, but with support for transparency.

    """

    @abstractmethod
    def render_strips(
        self, widget: Widget, width: int, height: int | None, style: Style
    ) -> list[Strip]:
        """Render the visual in to an iterable of strips.

        Args:
            base_style: The base style.
            width: Width of desired render.
            height: Height of desired render or `None` for any height.
            style: A Visual Style.

        Returns:
            An list of Strips.
        """

    @abstractmethod
    def get_optimal_width(self, container_width: int) -> int:
        """Get ideal width of the renderable to display its content.

        Args:
            container_size: The size of the container.

        Returns:
            A width in cells.

        """

    @abstractmethod
    def get_height(self, width: int) -> int:
        """Get the height of the visual if rendered with the given width.

        Returns:
            A height in lines.
        """

    @classmethod
    def to_strips(
        cls,
        widget: Widget,
        visual: Visual,
        width: int,
        height: int | None,
        style: Style,
        *,
        pad: bool = False,
        align: tuple[AlignHorizontal, AlignVertical] = ("left", "top"),
    ) -> list[Strip]:
        """High level function to render a visual to strips.

        Args:
            widget: Widget that produced the visual.
            visual: A Visual instance.
            width: Desired width (in cells).
            height: Desired height (in lines) or `None` for no limit.
            style: A (Visual) Style instance.
            pad: Pad to desired width?
            align: Tuple of horizontal and vertical alignment.

        Returns:
            A list of Strips containing the render.
        """
        strips = visual.render_strips(widget, width, height, style)
        if height is None:
            height = len(strips)
        rich_style = style.rich_style
        if pad:
            strips = [strip.extend_cell_length(width, rich_style) for strip in strips]
        if align != ("left", "top"):
            align_horizontal, align_vertical = align
            strips = list(
                Strip.align(
                    strips,
                    rich_style,
                    width,
                    height,
                    align_horizontal,
                    align_vertical,
                )
            )

        return strips


@rich.repr.auto
class RichVisual(Visual):
    """A Visual to wrap a Rich renderable."""

    def __init__(self, widget: Widget, renderable: RenderableType) -> None:
        """

        Args:
            widget: The associated Widget.
            renderable: A Rich renderable.
        """
        self._widget = widget
        self._renderable = renderable
        self._measurement: Measurement | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._widget
        yield self._renderable

    def _measure(self, console: Console, options: ConsoleOptions) -> Measurement:
        if self._measurement is None:
            self._measurement = Measurement.get(
                console,
                options,
                self._widget.post_render(self._renderable, RichStyle.null()),
            )
        return self._measurement

    def get_optimal_width(self, container_width: int) -> int:
        console = active_app.get().console
        width = measure(
            console, self._renderable, container_width, container_width=container_width
        )

        return width

    def get_height(self, width: int) -> int:
        console = active_app.get().console
        renderable = self._renderable
        if isinstance(renderable, Text):
            height = len(
                Text(renderable.plain).wrap(
                    console,
                    width,
                    no_wrap=renderable.no_wrap,
                    tab_size=renderable.tab_size or 8,
                )
            )
        else:
            options = console.options.update_width(width).update(highlight=False)
            segments = console.render(renderable, options)
            # Cheaper than counting the lines returned from render_lines!
            height = sum([text.count("\n") for text, _, _ in segments])

        return height

    def render_strips(
        self,
        widget: Widget,
        width: int,
        height: int | None,
        style: Style,
    ) -> list[Strip]:
        console = active_app.get().console
        options = console.options.update(
            highlight=False,
            width=width,
            height=height,
        )
        rich_style = style.rich_style
        renderable = widget.post_render(self._renderable, rich_style)
        segments = console.render(renderable, options.update_width(width))
        strips = [
            Strip(line)
            for line in islice(
                Segment.split_and_crop_lines(
                    segments, width, include_new_lines=False, pad=False
                ),
                None,
                height,
            )
        ]
        return strips


@rich.repr.auto
class Padding(Visual):
    """A Visual to pad another visual."""

    def __init__(self, visual: Visual, spacing: Spacing):
        """

        Args:
            Visual: A Visual.
            spacing: A Spacing object containing desired padding dimensions.
        """
        self._visual = visual
        self._spacing = spacing

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._visual
        yield self._spacing

    def get_optimal_width(self, container_width: int) -> int:
        return self._visual.get_optimal_width(container_width) + self._spacing.width

    def get_height(self, width: int) -> int:
        return self._visual.get_height(width) + self._spacing.height

    def render_strips(
        self,
        widget: Widget,
        width: int,
        height: int | None,
        style: Style,
    ) -> list[Strip]:
        padding = self._spacing
        top, right, bottom, left = self._spacing
        render_width = width - (left + right)
        if render_width <= 0:
            return []
        strips = self._visual.render_strips(
            widget,
            render_width,
            None if height is None else height - padding.height,
            style,
        )

        if padding:
            rich_style = style.rich_style
            top_padding = [Strip.blank(width, rich_style)] * top if top else []
            bottom_padding = [Strip.blank(width, rich_style)] * bottom if bottom else []
            strips = [
                *top_padding,
                *[
                    strip.crop_pad(render_width, left, right, rich_style)
                    for strip in strips
                ],
                *bottom_padding,
            ]

        return strips
