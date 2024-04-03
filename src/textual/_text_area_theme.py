from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from rich.style import Style

from textual.app import DEFAULT_COLORS
from textual.color import Color
from textual.design import DEFAULT_DARK_SURFACE

if TYPE_CHECKING:
    from textual.widgets import TextArea


@dataclass
class TextAreaTheme:
    """A theme for the `TextArea` widget.

    Allows theming the general widget (gutter, selections, cursor, and so on) and
    mapping of tree-sitter tokens to Rich styles.

    For example, consider the following snippet from the `markdown.scm` highlight
    query file. We've assigned the `heading_content` token type to the name `heading`.

    ```
    (heading_content) @heading
    ```

    Now, we can map this `heading` name to a Rich style, and it will be styled as
    such in the `TextArea`, assuming a parser which returns a `heading_content`
    node is used (as will be the case when language="markdown").

    ```
    TextAreaTheme('my_theme', syntax_styles={'heading': Style(color='cyan', bold=True)})
    ```

    We can register this theme with our `TextArea` using the  [`TextArea.register_theme`][textual.widgets._text_area.TextArea.register_theme] method,
    and headings in our markdown files will be styled bold cyan.
    """

    name: str
    """The name of the theme."""

    base_style: Style | None = None
    """The background style of the text area. If `None` the parent style will be used."""

    gutter_style: Style | None = None
    """The style of the gutter. If `None`, a legible Style will be generated."""

    cursor_style: Style | None = None
    """The style of the cursor. If `None`, a legible Style will be generated."""

    cursor_line_style: Style | None = None
    """The style to apply to the line the cursor is on."""

    cursor_line_gutter_style: Style | None = None
    """The style to apply to the gutter of the line the cursor is on. If `None`, a legible Style will be
    generated."""

    bracket_matching_style: Style | None = None
    """The style to apply to matching brackets. If `None`, a legible Style will be generated."""

    selection_style: Style | None = None
    """The style of the selection. If `None` a default selection Style will be generated."""

    syntax_styles: dict[str, Style] = field(default_factory=dict)
    """The mapping of tree-sitter names from the `highlight_query` to Rich styles."""

    _theme_configured_attributes: set[str] = field(init=False, default_factory=set)
    """Records which attributes were set via the theme object (as opposed to CSS components)."""

    def __post_init__(self) -> None:
        theme_fields = fields(self)
        for field in theme_fields:
            if getattr(self, field.name) is not None:
                self._theme_configured_attributes.add(field.name)

    def apply_css(self, text_area: TextArea) -> None:
        """Apply CSS rules from a TextArea to be used for fallback styling.

        If any attributes in the theme aren't supplied, they'll be filled with the appropriate
        base CSS (e.g. color, background, etc.) and component CSS (e.g. text-area--cursor) from
        the supplied TextArea.

        Args:
            text_area: The TextArea instance to retrieve fallback styling from.
        """
        self.base_style = text_area.rich_style or Style()
        get_style = text_area.get_component_rich_style

        if self.base_style.color is None:
            self.base_style = Style(color="#f3f3f3", bgcolor=self.base_style.bgcolor)

        if self.base_style.bgcolor is None:
            self.base_style = Style(
                color=self.base_style.color, bgcolor=DEFAULT_DARK_SURFACE
            )

        configured = self._theme_configured_attributes.__contains__

        assert self.base_style is not None
        assert self.base_style.color is not None
        assert self.base_style.bgcolor is not None

        if not configured("gutter_style"):
            gutter_style = get_style("text-area--gutter")
            if gutter_style:
                self.gutter_style = gutter_style
            else:
                self.gutter_style = self.base_style.copy()

        background_color = Color.from_rich_color(self.base_style.bgcolor)
        if not configured("cursor_style"):
            # If the theme doesn't contain a cursor style, fallback to component styles.
            cursor_style = get_style("text-area--cursor")
            if cursor_style:
                self.cursor_style = cursor_style
            else:
                # There's no component style either, fallback to a default.
                self.cursor_style = Style.from_color(
                    color=background_color.rich_color,
                    bgcolor=background_color.inverse.rich_color,
                )

        # Apply fallbacks for the styles of the active line and active line gutter.
        if not configured("cursor_line_style"):
            self.cursor_line_style = get_style("text-area--cursor-line")

        if not configured("cursor_line_gutter_style"):
            self.cursor_line_gutter_style = get_style("text-area--cursor-gutter")

        if not configured("bracket_matching_style"):
            matching_bracket_style = get_style("text-area--matching-bracket")
            if matching_bracket_style:
                self.bracket_matching_style = matching_bracket_style
            else:
                bracket_matching_background = background_color.blend(
                    background_color.inverse, factor=0.05
                )
                self.bracket_matching_style = Style(
                    bgcolor=bracket_matching_background.rich_color
                )

        if not configured("selection_style"):
            selection_style = get_style("text-area--selection")
            if selection_style:
                self.selection_style = selection_style
            else:
                selection_background_color = background_color.blend(
                    DEFAULT_COLORS["dark"].primary, factor=0.75
                )
                self.selection_style = Style.from_color(
                    bgcolor=selection_background_color.rich_color
                )

    @classmethod
    def get_builtin_theme(cls, theme_name: str) -> TextAreaTheme | None:
        """Get a `TextAreaTheme` by name.

        Given a `theme_name`, return the corresponding `TextAreaTheme` object.

        Args:
            theme_name: The name of the theme.

        Returns:
            The `TextAreaTheme` corresponding to the name or `None` if the theme isn't
                found.
        """
        return _BUILTIN_THEMES.get(theme_name)

    def get_highlight(self, name: str) -> Style | None:
        """Return the Rich style corresponding to the name defined in the tree-sitter
        highlight query for the current theme.

        Args:
            name: The name of the highlight.

        Returns:
            The `Style` to use for this highlight, or `None` if no style.
        """
        return self.syntax_styles.get(name)

    @classmethod
    def builtin_themes(cls) -> list[TextAreaTheme]:
        """Get a list of all builtin TextAreaThemes.

        Returns:
            A list of all builtin TextAreaThemes.
        """
        return list(_BUILTIN_THEMES.values())


_MONOKAI = TextAreaTheme(
    name="monokai",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    cursor_style=Style(color="#272822", bgcolor="#f8f8f0"),
    cursor_line_style=Style(bgcolor="#3e3d32"),
    cursor_line_gutter_style=Style(color="#c2c2bf", bgcolor="#3e3d32"),
    bracket_matching_style=Style(bgcolor="#838889", bold=True),
    selection_style=Style(bgcolor="#65686a"),
    syntax_styles={
        "string": Style(color="#E6DB74"),
        "string.documentation": Style(color="#E6DB74"),
        "comment": Style(color="#75715E"),
        "keyword": Style(color="#F92672"),
        "operator": Style(color="#F92672"),
        "repeat": Style(color="#F92672"),
        "exception": Style(color="#F92672"),
        "include": Style(color="#F92672"),
        "keyword.function": Style(color="#F92672"),
        "keyword.return": Style(color="#F92672"),
        "keyword.operator": Style(color="#F92672"),
        "conditional": Style(color="#F92672"),
        "number": Style(color="#AE81FF"),
        "float": Style(color="#AE81FF"),
        "class": Style(color="#A6E22E"),
        "type.class": Style(color="#A6E22E"),
        "function": Style(color="#A6E22E"),
        "function.call": Style(color="#A6E22E"),
        "method": Style(color="#A6E22E"),
        "method.call": Style(color="#A6E22E"),
        "boolean": Style(color="#66D9EF", italic=True),
        "constant.builtin": Style(color="#66D9EF", italic=True),
        "json.null": Style(color="#66D9EF", italic=True),
        "regex.punctuation.bracket": Style(color="#F92672"),
        "regex.operator": Style(color="#F92672"),
        "html.end_tag_error": Style(color="red", underline=True),
        "tag": Style(color="#F92672"),
        "yaml.field": Style(color="#F92672", bold=True),
        "json.label": Style(color="#F92672", bold=True),
        "toml.type": Style(color="#F92672"),
        "toml.datetime": Style(color="#AE81FF"),
        "heading": Style(color="#F92672", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#66D9EF", underline=True),
        "inline_code": Style(color="#E6DB74"),
    },
)

_DRACULA = TextAreaTheme(
    name="dracula",
    base_style=Style(color="#f8f8f2", bgcolor="#1E1F35"),
    gutter_style=Style(color="#6272a4"),
    cursor_style=Style(color="#282a36", bgcolor="#f8f8f0"),
    cursor_line_style=Style(bgcolor="#282b45"),
    cursor_line_gutter_style=Style(color="#c2c2bf", bgcolor="#282b45", bold=True),
    bracket_matching_style=Style(bgcolor="#99999d", bold=True, underline=True),
    selection_style=Style(bgcolor="#44475A"),
    syntax_styles={
        "string": Style(color="#f1fa8c"),
        "string.documentation": Style(color="#f1fa8c"),
        "comment": Style(color="#6272a4"),
        "keyword": Style(color="#ff79c6"),
        "operator": Style(color="#ff79c6"),
        "repeat": Style(color="#ff79c6"),
        "exception": Style(color="#ff79c6"),
        "include": Style(color="#ff79c6"),
        "keyword.function": Style(color="#ff79c6"),
        "keyword.return": Style(color="#ff79c6"),
        "keyword.operator": Style(color="#ff79c6"),
        "conditional": Style(color="#ff79c6"),
        "number": Style(color="#bd93f9"),
        "float": Style(color="#bd93f9"),
        "class": Style(color="#50fa7b"),
        "type.class": Style(color="#50fa7b"),
        "function": Style(color="#50fa7b"),
        "function.call": Style(color="#50fa7b"),
        "method": Style(color="#50fa7b"),
        "method.call": Style(color="#50fa7b"),
        "boolean": Style(color="#bd93f9"),
        "constant.builtin": Style(color="#bd93f9"),
        "json.null": Style(color="#bd93f9"),
        "regex.punctuation.bracket": Style(color="#ff79c6"),
        "regex.operator": Style(color="#ff79c6"),
        "html.end_tag_error": Style(color="#F83333", underline=True),
        "tag": Style(color="#ff79c6"),
        "yaml.field": Style(color="#ff79c6", bold=True),
        "json.label": Style(color="#ff79c6", bold=True),
        "toml.type": Style(color="#ff79c6"),
        "toml.datetime": Style(color="#bd93f9"),
        "heading": Style(color="#ff79c6", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#bd93f9", underline=True),
        "inline_code": Style(color="#f1fa8c"),
    },
)

_DARK_VS = TextAreaTheme(
    name="vscode_dark",
    base_style=Style(color="#CCCCCC", bgcolor="#1F1F1F"),
    gutter_style=Style(color="#6E7681", bgcolor="#1F1F1F"),
    cursor_style=Style(color="#1e1e1e", bgcolor="#f0f0f0"),
    cursor_line_style=Style(bgcolor="#2b2b2b"),
    bracket_matching_style=Style(bgcolor="#3a3a3a", bold=True),
    cursor_line_gutter_style=Style(color="#CCCCCC", bgcolor="#2b2b2b"),
    selection_style=Style(bgcolor="#264F78"),
    syntax_styles={
        "string": Style(color="#ce9178"),
        "string.documentation": Style(color="#ce9178"),
        "comment": Style(color="#6A9955"),
        "keyword": Style(color="#569cd6"),
        "operator": Style(color="#569cd6"),
        "conditional": Style(color="#569cd6"),
        "keyword.function": Style(color="#569cd6"),
        "keyword.return": Style(color="#569cd6"),
        "keyword.operator": Style(color="#569cd6"),
        "repeat": Style(color="#569cd6"),
        "exception": Style(color="#569cd6"),
        "include": Style(color="#569cd6"),
        "number": Style(color="#b5cea8"),
        "float": Style(color="#b5cea8"),
        "class": Style(color="#4EC9B0"),
        "type.class": Style(color="#4EC9B0"),
        "function": Style(color="#4EC9B0"),
        "function.call": Style(color="#4EC9B0"),
        "method": Style(color="#4EC9B0"),
        "method.call": Style(color="#4EC9B0"),
        "boolean": Style(color="#7DAF9C"),
        "constant.builtin": Style(color="#7DAF9C"),
        "json.null": Style(color="#7DAF9C"),
        "tag": Style(color="#EFCB43"),
        "yaml.field": Style(color="#569cd6", bold=True),
        "json.label": Style(color="#569cd6", bold=True),
        "toml.type": Style(color="#569cd6"),
        "heading": Style(color="#569cd6", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#40A6FF", underline=True),
        "inline_code": Style(color="#ce9178"),
        "info_string": Style(color="#ce9178", bold=True, italic=True),
    },
)

_GITHUB_LIGHT = TextAreaTheme(
    name="github_light",
    base_style=Style(color="#24292e", bgcolor="#f0f0f0"),
    gutter_style=Style(color="#BBBBBB", bgcolor="#f0f0f0"),
    cursor_style=Style(color="#fafbfc", bgcolor="#24292e"),
    cursor_line_style=Style(bgcolor="#ebebeb"),
    bracket_matching_style=Style(color="#24292e", underline=True),
    cursor_line_gutter_style=Style(color="#A4A4A4", bgcolor="#ebebeb"),
    selection_style=Style(bgcolor="#c8c8fa"),
    syntax_styles={
        "string": Style(color="#093069"),
        "string.documentation": Style(color="#093069"),
        "comment": Style(color="#6a737d"),
        "keyword": Style(color="#d73a49"),
        "operator": Style(color="#0450AE"),
        "conditional": Style(color="#CF222E"),
        "keyword.function": Style(color="#CF222E"),
        "keyword.return": Style(color="#CF222E"),
        "keyword.operator": Style(color="#CF222E"),
        "repeat": Style(color="#CF222E"),
        "exception": Style(color="#CF222E"),
        "include": Style(color="#CF222E"),
        "number": Style(color="#d73a49"),
        "float": Style(color="#d73a49"),
        "parameter": Style(color="#24292e"),
        "class": Style(color="#963800"),
        "variable": Style(color="#e36209"),
        "function": Style(color="#6639BB"),
        "method": Style(color="#6639BB"),
        "boolean": Style(color="#7DAF9C"),
        "constant.builtin": Style(color="#7DAF9C"),
        "tag": Style(color="#6639BB"),
        "yaml.field": Style(color="#6639BB"),
        "json.label": Style(color="#6639BB"),
        "toml.type": Style(color="#6639BB"),
        "heading": Style(color="#24292e", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#40A6FF", underline=True),
        "inline_code": Style(color="#093069"),
    },
)

_CSS_THEME = TextAreaTheme(name="css", syntax_styles=_DARK_VS.syntax_styles)

_BUILTIN_THEMES = {
    "css": _CSS_THEME,
    "monokai": _MONOKAI,
    "dracula": _DRACULA,
    "vscode_dark": _DARK_VS,
    "github_light": _GITHUB_LIGHT,
}
