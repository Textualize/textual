"""
The Style class contains all the information needed to generate styled terminal output.

You won't often need to create Style objects directly, if you are using [Content][textual.content.Content] for output.
But you might want to use styles for more customized widgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, lru_cache
from operator import attrgetter
from pickle import dumps, loads
from typing import TYPE_CHECKING, Any, Iterable, Mapping

import rich.repr
from rich.style import Style as RichStyle
from rich.terminal_theme import TerminalTheme

from textual._context import active_app
from textual.color import Color

if TYPE_CHECKING:
    from textual.css.styles import StylesBase


_get_hash_attributes = attrgetter(
    "background",
    "foreground",
    "bold",
    "dim",
    "italic",
    "underline",
    "underline2",
    "reverse",
    "strike",
    "blink",
    "link",
    "auto_color",
    "_meta",
)


_get_simple_attributes = attrgetter(
    "background",
    "foreground",
    "bold",
    "dim",
    "italic",
    "underline",
    "underline2",
    "reverse",
    "strike",
    "blink",
    "link",
    "_meta",
)

_get_simple_attributes_sans_color = attrgetter(
    "bold",
    "dim",
    "italic",
    "underline",
    "underline2",
    "reverse",
    "strike",
    "blink",
    "link",
    "_meta",
)


_get_attributes = attrgetter(
    "background",
    "foreground",
    "bold",
    "dim",
    "italic",
    "underline",
    "underline2",
    "reverse",
    "strike",
    "blink",
    "link",
    "meta",
    "_meta",
)


@rich.repr.auto()
@dataclass(frozen=True)
class Style:
    """Represents a style in the Visual interface (color and other attributes).

    Styles may be added together, which combines their style attributes.

    """

    background: Color | None = None
    foreground: Color | None = None
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    underline2: bool | None = None
    reverse: bool | None = None
    strike: bool | None = None
    blink: bool | None = None
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
        yield "underline2", self.underline2, None
        yield "reverse", self.reverse, None
        yield "strike", self.strike, None
        yield "blink", self.blink, None
        yield "link", self.link, None

        if self._meta is not None:
            yield "meta", self.meta

    @cached_property
    def _is_null(self) -> bool:
        return _get_simple_attributes(self) == (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @cached_property
    def hash(self) -> int:
        """A hash of the style's attributes."""
        return hash(_get_hash_attributes(self))

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Style):
            return NotImplemented
        return self.hash == other.hash

    def __bool__(self) -> bool:
        return not self._is_null

    def __str__(self) -> str:
        return self.style_definition

    @cached_property
    def style_definition(self) -> str:
        """Style encoded in a string (may be parsed from `Style.parse`)."""
        output: list[str] = []
        output_append = output.append
        if self.foreground is not None:
            output_append(self.foreground.css)
        if self.background is not None:
            output_append(f"on {self.background.css}")
        if self.bold is not None:
            output_append("bold" if self.bold else "not bold")
        if self.dim is not None:
            output_append("dim" if self.dim else "not dim")
        if self.italic is not None:
            output_append("italic" if self.italic else "not italic")
        if self.underline is not None:
            output_append("underline" if self.underline else "not underline")
        if self.underline2 is not None:
            output_append("underline2" if self.underline2 else "not underline2")
        if self.strike is not None:
            output_append("strike" if self.strike else "not strike")
        if self.blink is not None:
            output_append("blink" if self.blink else "not blink")
        if self.link is not None:
            if "'" not in self.link:
                output_append(f"link='{self.link}'")
            elif '"' not in self.link:
                output_append(f'link="{self.link}"')
        if self._meta is not None:
            for key, value in self.meta.items():
                if isinstance(value, str):
                    if "'" not in key:
                        output_append(f"{key}='{value}'")
                    elif '"' not in key:
                        output_append(f'{key}="{value}"')
                    else:
                        output_append(f"{key}={value!r}")
                else:
                    output_append(f"{key}={value!r}")

        return " ".join(output)

    @cached_property
    def markup_tag(self) -> str:
        """Identifier used to close tags in markup."""
        output: list[str] = []
        output_append = output.append
        if self.foreground is not None:
            output_append(self.foreground.css)
        if self.background is not None:
            output_append(f"on {self.background.css}")
        if self.bold is not None:
            output_append("bold" if self.bold else "not bold")
        if self.dim is not None:
            output_append("dim" if self.dim else "not dim")
        if self.italic is not None:
            output_append("italic" if self.italic else "not italic")
        if self.underline is not None:
            output_append("underline" if self.underline else "not underline")
        if self.underline2 is not None:
            output_append("underline2" if self.underline2 else "not underline2")
        if self.strike is not None:
            output_append("strike" if self.strike else "not strike")
        if self.blink is not None:
            output_append("blink" if self.blink else "not blink")
        if self.link is not None:
            output_append("link")
        if self._meta is not None:
            for key, value in self.meta.items():
                if isinstance(value, str):
                    output_append(f"{key}=")

        return " ".join(output)

    @lru_cache(maxsize=1024 * 4)
    def __add__(self, other: object | None) -> Style:
        if isinstance(other, Style):
            if self._is_null:
                return other
            if other._is_null:
                return self
            (
                background,
                foreground,
                bold,
                dim,
                italic,
                underline,
                underline2,
                reverse,
                strike,
                blink,
                link,
                meta,
                _meta,
            ) = _get_attributes(self)

            (
                other_background,
                other_foreground,
                other_bold,
                other_dim,
                other_italic,
                other_underline,
                other_underline2,
                other_reverse,
                other_strike,
                other_blink,
                other_link,
                other_meta,
                other__meta,
            ) = _get_attributes(other)

            new_style = Style(
                (
                    other_background
                    if (background is None or background.a == 0)
                    else background + other_background
                ),
                (
                    foreground
                    if (other_foreground is None or other_foreground.a == 0)
                    else other_foreground
                ),
                bold if other_bold is None else other_bold,
                dim if other_dim is None else other_dim,
                italic if other_italic is None else other_italic,
                underline if other_underline is None else other_underline,
                underline2 if other_underline2 is None else other_underline2,
                reverse if other_reverse is None else other_reverse,
                strike if other_strike is None else other_strike,
                blink if other_blink is None else other_blink,
                link if other_link is None else other_link,
                (
                    dumps({**meta, **other_meta})
                    if _meta is not None and other__meta is not None
                    else (_meta if other__meta is None else other__meta)
                ),
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
        """Parse a style from text.

        Args:
            text_style: A style encoded in a string.
            variables: Optional mapping of CSS variables. `None` to get variables from the app.

        Returns:
            New style.
        """
        from textual.markup import parse_style

        try:
            app = active_app.get()
        except LookupError:
            return parse_style(text_style, variables)
        return app.stylesheet.parse_style(text_style)

    @classmethod
    def _normalize_markup_tag(cls, text_style: str) -> str:
        """Produces a normalized from of a style, used to match closing tags with opening tags.

        Args:
            text_style: Style to normalize.

        Returns:
            Normalized markup tag.
        """
        try:
            style = cls.parse(text_style)
        except Exception:
            return text_style.strip()
        return style.markup_tag

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
            underline2=rich_style.underline2,
            reverse=rich_style.reverse,
            strike=rich_style.strike,
            blink=rich_style.blink,
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
            underline2=text_style.underline2,
            reverse=text_style.reverse,
            strike=text_style.strike,
            blink=text_style.blink,
            auto_color=styles.auto_color,
        )

    @classmethod
    def from_meta(cls, meta: Mapping[str, Any]) -> Style:
        """Create a Visual Style containing meta information.

        Args:
            meta: A dictionary of meta information.

        Returns:
            A new Style.
        """
        return Style(_meta=dumps({**meta}))

    @cached_property
    def rich_style(self) -> RichStyle:
        """Convert this Styles into a Rich style.

        Returns:
            A Rich style object.
        """

        (
            background,
            foreground,
            bold,
            dim,
            italic,
            underline,
            underline2,
            reverse,
            strike,
            blink,
            link,
            _meta,
        ) = _get_simple_attributes(self)

        color = None if foreground is None else background + foreground

        return RichStyle(
            color=None if color is None else color.rich_color,
            bgcolor=None if background is None else background.rich_color,
            bold=bold,
            dim=dim,
            italic=italic,
            underline=underline,
            underline2=underline2,
            reverse=reverse,
            strike=strike,
            blink=blink,
            link=link,
            meta=None if _meta is None else self.meta,
        )

    def rich_style_with_offset(self, x: int, y: int) -> RichStyle:
        """Get a Rich style with the given offset included in meta.

        This is used in text selection.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            A Rich Style object.
        """
        (
            background,
            foreground,
            bold,
            dim,
            italic,
            underline,
            underline2,
            reverse,
            strike,
            blink,
            link,
            _meta,
        ) = _get_simple_attributes(self)
        color = None if foreground is None else background + foreground
        return RichStyle(
            color=None if color is None else color.rich_color,
            bgcolor=None if background is None else background.rich_color,
            bold=bold,
            dim=dim,
            italic=italic,
            underline=underline,
            underline2=underline2,
            reverse=reverse,
            strike=strike,
            blink=blink,
            link=link,
            meta={**self.meta, "offset": (x, y)},
        )

    @cached_property
    def without_color(self) -> Style:
        """The style without any colors."""
        return Style(None, None, *_get_simple_attributes_sans_color(self))

    @cached_property
    def background_style(self) -> Style:
        """Just the background color, with no other attributes."""
        return Style(self.background, _meta=self._meta)

    @property
    def has_transparent_foreground(self) -> bool:
        """Is the foreground transparent (or not set)?"""
        return self.foreground is None or self.foreground.a == 0

    @classmethod
    def combine(cls, styles: Iterable[Style]) -> Style:
        """Add a number of styles and get the result."""
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @cached_property
    def meta(self) -> Mapping[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else loads(self._meta)


NULL_STYLE = Style()
