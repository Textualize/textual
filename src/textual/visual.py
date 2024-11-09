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
from rich.text import Text

from textual._context import active_app
from textual.color import TRANSPARENT, Color
from textual.css.styles import Styles
from textual.geometry import Spacing
from textual.strip import Strip

if TYPE_CHECKING:
    from textual.widget import Widget

_NULL_RICH_STYLE = RichStyle()


def is_visual(obj: object) -> bool:
    """Check if the given object is a Visual or supports the Visual protocol."""
    return isinstance(obj, Visual) or hasattr(obj, "textualize")


class SupportsTextualize(Protocol):
    """An object that supports the textualize protocol."""

    def textualize(self, obj: object) -> Visual | None: ...


class VisualError(Exception):
    """An error with the visual protocol."""


VisualType = RenderableType | SupportsTextualize | "Visual"


def visualize(widget: Widget, obj: object) -> Visual:
    """Get a visual instance from an object.

    Args:
        obj: An object.

    Returns:
        A Visual instance to render the object, or `None` if there is no associated visual.
    """
    if isinstance(obj, Visual):
        # Already a visual
        return obj
    visualize = getattr(obj, "visualize", None)
    if visualize is None:
        # Doesn't expose the textualize protocol
        if is_renderable(obj):
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
    """Represent a content style (color and other attributes)."""

    background: Color = TRANSPARENT
    foreground: Color = TRANSPARENT
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    link: str | None = None
    _meta: bytes | None = None

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
    def from_rich_style(cls, rich_style: RichStyle) -> Style:
        return Style(
            Color.from_rich_color(rich_style.bgcolor),
            Color.from_rich_color(rich_style.color),
            bold=rich_style.bold,
            dim=rich_style.dim,
            italic=rich_style.italic,
            underline=rich_style.underline,
            strike=rich_style.strike,
        )

    @classmethod
    def from_styles(cls, styles: Styles) -> Style:
        text_style = styles.text_style
        return Style(
            styles.background,
            styles.color,
            bold=text_style.bold,
            dim=text_style.italic,
            italic=text_style.italic,
            underline=text_style.underline,
            strike=text_style.strike,
        )

    @cached_property
    def rich_style(self) -> RichStyle:
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
            height: Height of desired render.

        Returns:
            An iterable of Strips.
        """

    @abstractmethod
    def get_optimal_width(self, tab_size: int = 8) -> int:
        """Get ideal width of the renderable to display its content.

        Args:
            tab_size: Size of tabs.

        Returns:
            A width in cells.

        """

    @abstractmethod
    def get_minimal_width(self, tab_size: int = 8) -> int:
        """Get the minimal width (the small width that doesn't lose information).

        Args:
            tab_size: Size of tabs.

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
        visual: Visual,
        width: int,
        height: int,
        widget: Widget,
        component_classes: list[str] | None = None,
    ) -> list[Strip]:
        visual_style = (
            widget.get_visual_style(*component_classes)
            if component_classes
            else widget.get_visual_style()
        )
        strips = visual.render_strips(widget, width, height, visual_style)
        return strips


@rich.repr.auto
class RichVisual(Visual):
    def __init__(self, widget: Widget, renderable: RenderableType) -> None:
        self._widget = widget
        self._renderable = renderable
        self._post_renderable: RenderableType | None = None
        self._measurement: Measurement | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._widget
        yield self._renderable

    def _measure(self, console: Console, options: ConsoleOptions) -> Measurement:
        if self._measurement is None:
            self._measurement = Measurement.get(console, options, self._renderable)
        return self._measurement

    def get_optimal_width(self, tab_size: int = 8) -> int:
        console = active_app.get().console
        measurement = self._measure(console, console.options)
        return measurement.maximum

    def get_minimal_width(self, tab_size: int = 8) -> int:
        console = active_app.get().console
        measurement = self._measure(console, console.options)
        return measurement.minimum

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
        if self._post_renderable is None:
            self._post_renderable = widget.post_render(self._renderable)
        renderable = self._post_renderable

        segments = console.render(renderable, options)
        rich_style = style.rich_style
        if rich_style:
            segments = Segment.apply_style(segments, post_style=rich_style)

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


class Padding(Visual):
    def __init__(self, visual: Visual, spacing: Spacing):
        self._visual = visual
        self._spacing = spacing

    def get_optimal_width(self, tab_size: int = 8) -> int:
        return self._visual.get_optimal_width(tab_size) + self._spacing.width

    def get_minimal_width(self, tab_size: int = 8) -> int:
        return self._visual.get_minimal_width(tab_size) + self._spacing.width

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
        strips = self._visual.render_strips(
            widget,
            render_width,
            None if height is None else height - padding.height,
            style,
        )
        rich_style = style.rich_style
        if padding:
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
