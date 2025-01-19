from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, lru_cache
from marshal import dumps, loads
from typing import TYPE_CHECKING, Any, Iterable

import rich.repr
from rich.style import Style as RichStyle
from rich.terminal_theme import TerminalTheme

from textual.color import Color

if TYPE_CHECKING:
    from textual.css.styles import StylesBase


@rich.repr.auto(angular=True)
@dataclass(frozen=True)
class Style:
    """Represents a style in the Visual interface (color and other attributes)."""

    background: Color | None = None
    foreground: Color | None = None
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    reverse: bool | None = None
    strike: bool | None = None
    link: str | None = None
    _meta: bytes | None = None
    auto_color: bool = False

    def __rich_repr__(self) -> rich.repr.Result:
        yield "background", self.background, None
        yield "foreground", self.foreground, None
        yield "bold", self.bold, None
        yield "dim", self.dim, None
        yield "italic", self.italic, None
        yield "underline", self.underline, None
        yield "reverse", self.reverse, None
        yield "strike", self.strike, None
        yield "link", self.link, None

        if self._meta is not None:
            yield "meta", self.meta

    @cached_property
    def _is_null(self) -> bool:
        return (
            self.foreground is None
            and self.background is None
            and self.bold is None
            and self.dim is None
            and self.italic is None
            and self.underline is None
            and self.reverse is None
            and self.strike is None
            and self.link is None
            and self._meta is None
        )

    def __bool__(self) -> bool:
        return not self._is_null

    def __str__(self) -> str:
        output: list[str] = []
        if self.foreground is not None:
            output.append(self.foreground.css)
        if self.background is not None:
            output.append(f"on {self.background.css}")
        if self.bold is not None:
            output.append("bold" if self.bold else "not bold")
        if self.dim is not None:
            output.append("dim" if self.dim else "not dim")
        if self.italic is not None:
            output.append("italic" if self.italic else "not italic")
        if self.underline is not None:
            output.append("underline" if self.underline else "not underline")
        if self.strike is not None:
            output.append("strike" if self.strike else "not strike")

        return " ".join(output)

    @lru_cache(maxsize=1024)
    def __add__(self, other: object | None) -> Style:
        if isinstance(other, Style):
            new_style = Style(
                (
                    other.background
                    if self.background is None
                    else self.background + other.background
                ),
                # other.foreground if self.foreground is None else None,
                self.foreground if other.foreground is None else other.foreground,
                self.bold if other.bold is None else other.bold,
                self.dim if other.dim is None else other.dim,
                self.italic if other.italic is None else other.italic,
                self.underline if other.underline is None else other.underline,
                self.reverse if other.reverse is None else other.reverse,
                self.strike if other.strike is None else other.strike,
                self.link if other.link is None else other.link,
                self._meta if other._meta is None else other._meta,
            )
            return new_style
        elif other is None:
            return self
        else:
            return NotImplemented

    __radd__ = __add__

    @classmethod
    def null(cls) -> Style:
        """Get a null (no color or style) style."""
        return NULL_STYLE

    @classmethod
    def parse(cls, text_style: str, variables: dict[str, str] | None = None) -> Style:
        from textual._style_parse import style_parse

        return style_parse(text_style, {} if variables is None else variables)

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
            (
                None
                if rich_style.bgcolor is None
                else Color.from_rich_color(rich_style.bgcolor, theme)
            ),
            (
                None
                if rich_style.color is None
                else Color.from_rich_color(rich_style.color, theme)
            ),
            bold=rich_style.bold,
            dim=rich_style.dim,
            italic=rich_style.italic,
            underline=rich_style.underline,
            reverse=rich_style.reverse,
            strike=rich_style.strike,
            link=rich_style.link,
            _meta=rich_style._meta,
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
            reverse=text_style.reverse,
            strike=text_style.strike,
            auto_color=styles.auto_color,
        )

    @classmethod
    def from_meta(cls, meta: dict[str, object]) -> Style:
        """Create a Visual Style containing meta information.

        Args:
            meta: A dictionary of meta information.

        Returns:
            A new Style.
        """
        return Style(_meta=dumps(meta))

    @cached_property
    def rich_style(self) -> RichStyle:
        """Convert this Styles into a Rich style.

        Returns:
            A Rich style object.
        """
        color = None if self.foreground is None else self.background + self.foreground
        return RichStyle(
            color=None if color is None else color.rich_color,
            bgcolor=None if self.background is None else self.background.rich_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            reverse=self.reverse,
            strike=self.strike,
            link=self.link,
            meta=None if self._meta is None else self.meta,
        )

    def rich_style_with_offset(self, x: int, y: int) -> RichStyle:
        color = None if self.foreground is None else self.background + self.foreground
        return RichStyle(
            color=None if color is None else color.rich_color,
            bgcolor=None if self.background is None else self.background.rich_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            reverse=self.reverse,
            strike=self.strike,
            link=self.link,
            meta={**self.meta, "offset": (x, y)},
        )

    @cached_property
    def without_color(self) -> Style:
        """The style with no color."""
        return Style(
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            reverse=self.reverse,
            strike=self.strike,
            link=self.link,
            _meta=self._meta,
        )

    @cached_property
    def background_style(self) -> Style:
        """Just the background color, with no other attributes."""
        return Style(self.background, _meta=self._meta)

    @classmethod
    def combine(cls, styles: Iterable[Style]) -> Style:
        """Add a number of styles and get the result."""
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @property
    def meta(self) -> dict[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else loads(self._meta)


NULL_STYLE = Style()
