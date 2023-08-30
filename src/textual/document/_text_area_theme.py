from __future__ import annotations

from dataclasses import dataclass, field

from rich.style import Style

from textual.color import Color


@dataclass
class TextAreaTheme:
    """Maps tree-sitter names to Rich styles for syntax-highlighting in `TextArea`.

    For example, consider the following snippet from the `markdown.scm` highlight
    query file. We've assigned the `heading_content` token type to the name `heading`.

    ```
    (heading_content) @heading
    ```

    Now, we can map this `heading` name to a Rich style, and it will be styled as
    such in the `TextArea`, assuming a parser which returns a `heading_content`
    node is used (as will be the case when language="markdown"):

    ```
    SyntaxTheme('my_theme', {'heading': Style(color='cyan', bold=True)})
    ```
    """

    name: str | None = None
    """The name of the theme."""

    token_styles: dict[str, TextAreaStyle] = field(default_factory=dict)
    """The mapping of tree-sitter names from the `highlight_query` to Rich styles."""

    base_style: TextAreaStyle | None = None
    """The background style of the text area. If `None` the parent style will be used."""

    gutter_style: TextAreaStyle | None = None
    """The style of the gutter. If `None`, a legible TextAreaStyle will be generated."""

    cursor_style: TextAreaStyle | None = None
    """The style of the cursor. If `None`, the legible TextAreaStyle will be generated."""

    cursor_line_style: TextAreaStyle | None = None
    """The style to apply to the line the cursor is on. If `None`, a legible TextAreaStyle will be generated."""

    cursor_line_gutter_style: TextAreaStyle | None = None
    """The style to apply to the gutter of the line the cursor is on. If `None`, a legible TextAreaStyle will be
    generated."""

    bracket_matching_style: TextAreaStyle | None = None
    """The style to apply to matching brackets. If `None`, a legible TextAreaStyle will be generated."""

    selection_style: TextAreaStyle | None = None
    """The style of the selection. If `None` a default selection TextAreaStyle will be generated."""

    @classmethod
    def get_theme(cls, theme_name: str) -> "TextAreaTheme":
        """Get a `SyntaxTheme` by name.

        Given a `theme_name` return the corresponding `SyntaxTheme` object.

        Check the available `SyntaxTheme`s by calling `SyntaxTheme.available_themes()`.

        Args:
            theme_name: The name of the theme.

        Returns:
            The `SyntaxTheme` corresponding to the name.
        """
        return cls(theme_name, _BUILTIN_THEMES.get(theme_name, {}))

    def get_highlight(self, name: str) -> TextAreaTheme:
        """Return the Rich style corresponding to the name defined in the tree-sitter
        highlight query for the current theme.

        Args:
            name: The name of the highlight.

        Returns:
            The `Style` to use for this highlight.
        """
        return self.token_styles.get(name)

    @classmethod
    def available_themes(cls) -> list[TextAreaTheme]:
        """Get a list of all available SyntaxThemes.

        Returns:
            A list of all available SyntaxThemes.
        """
        return [
            TextAreaTheme(name, mapping) for name, mapping in _BUILTIN_THEMES.items()
        ]

    @classmethod
    def default(cls) -> TextAreaTheme:
        """Get the default syntax theme.

        Returns:
            The default SyntaxTheme (probably Monokai).
        """
        return DEFAULT_SYNTAX_THEME


@dataclass
class TextAreaStyle:
    foreground_color: str | Color = None
    background_color: str | Color = None
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False

    def __post_init__(self) -> None:
        self.background_color = Color.parse(self.background_color)
        self.foreground_color = Color.parse(self.foreground_color).blend(
            self.background_color, factor=1
        )

        # The default for tree-sitter tokens which aren't mapped to styles.
        self.default_style = Style(
            color=self.foreground_color.rich_color,
            bgcolor=self.background_color.rich_color,
            bold=self.bold,
            italic=self.italic,
            strike=self.strikethrough,
            underline=self.underline,
        )


_MONOKAI = TextAreaTheme(
    name="monokai",
    base_style=TextAreaStyle("#f8f8f2", "#272822"),
    gutter_style=TextAreaStyle("#90908a", "#272822"),
    cursor_style=TextAreaStyle("#f8f8f0"),
    cursor_line_style=TextAreaStyle(background_color="#3e3d32"),
    cursor_line_gutter_style=TextAreaStyle("#c2c2bf", "#3e3d32"),
    bracket_matching_style=TextAreaStyle("#414339"),
    selection_style=TextAreaStyle(background_color="#878b9180"),
    token_styles={
        "string": TextAreaStyle("#E6DB74"),
        "string.documentation": TextAreaStyle("#E6DB74"),
        "comment": TextAreaStyle("#75715E"),
        "keyword": TextAreaStyle("#F92672"),
        "operator": TextAreaStyle("#F92672"),
        "repeat": TextAreaStyle("#F92672"),
        "exception": TextAreaStyle("#F92672"),
        "include": TextAreaStyle("#F92672"),
        "keyword.function": TextAreaStyle("#F92672"),
        "keyword.return": TextAreaStyle("#F92672"),
        "keyword.operator": TextAreaStyle("#F92672"),
        "conditional": TextAreaStyle("#F92672"),
        "number": TextAreaStyle("#AE81FF"),
        "float": TextAreaStyle("#AE81FF"),
        "class": TextAreaStyle("#A6E22E"),
        "function": TextAreaStyle("#A6E22E"),
        "function.call": TextAreaStyle("#A6E22E"),
        "method": TextAreaStyle("#A6E22E"),
        "method.call": TextAreaStyle("#A6E22E"),
        "boolean": TextAreaStyle("#66D9EF", italic=True),
        "json.null": TextAreaStyle("#66D9EF", italic=True),
        # "constant": TextAreaStyle("#AE81FF"),
        # "variable": TextAreaStyle("white"),
        # "parameter": TextAreaStyle("cyan"),
        # "type": TextAreaStyle("cyan"),
        # "escape": TextAreaStyle("magenta"),
        # "error": TextAreaStyle("TextAreaStyle", "red"),
        "regex.punctuation.bracket": TextAreaStyle("#F92672"),
        "regex.operator": TextAreaStyle("#F92672"),
        # "json.error": _NULL_STYLE,
        "html.end_tag_error": TextAreaStyle("red", underline=True),
        "tag": TextAreaStyle("#F92672"),
        "yaml.field": TextAreaStyle("#F92672", bold=True),
        "json.label": TextAreaStyle("#F92672", bold=True),
        "toml.type": TextAreaStyle("#F92672"),
        "toml.datetime": TextAreaStyle("#AE81FF"),
        # "toml.error": _NULL_STYLE,
        "heading": TextAreaStyle("#F92672", bold=True),
        "bold": TextAreaStyle(bold=True),
        "italic": TextAreaStyle(italic=True),
        "strikethrough": TextAreaStyle(strikethrough=True),
        "link": TextAreaStyle("#66D9EF", underline=True),
        "inline_code": TextAreaStyle("#F92672"),
    },
)

# _DRACULA = {
#     "string": Style(color="#f1fa8c"),
#     "string.documentation": Style(color="#f1fa8c"),
#     "comment": Style(color="#6272a4"),
#     "keyword": Style(color="#ff79c6"),
#     "operator": Style(color="#ff79c6"),
#     "repeat": Style(color="#ff79c6"),
#     "exception": Style(color="#ff79c6"),
#     "include": Style(color="#ff79c6"),
#     "keyword.function": Style(color="#ff79c6"),
#     "keyword.return": Style(color="#ff79c6"),
#     "keyword.operator": Style(color="#ff79c6"),
#     "conditional": Style(color="#ff79c6"),
#     "number": Style(color="#bd93f9"),
#     "float": Style(color="#bd93f9"),
#     "class": Style(color="#50fa7b"),
#     "function": Style(color="#50fa7b"),
#     "function.call": Style(color="#50fa7b"),
#     "method": Style(color="#50fa7b"),
#     "method.call": Style(color="#50fa7b"),
#     "boolean": Style(color="#bd93f9"),
#     "json.null": Style(color="#bd93f9"),
#     # "constant": Style(color="#bd93f9"),
#     # "variable": Style(color="white"),
#     # "parameter": Style(color="cyan"),
#     # "type": Style(color="cyan"),
#     # "escape": Style(bgcolor="magenta"),
#     "regex.punctuation.bracket": Style(color="#ff79c6"),
#     "regex.operator": Style(color="#ff79c6"),
#     # "error": Style(color="black", bgcolor="red"),
#     "json.error": _NULL_STYLE,
#     "html.end_tag_error": Style(color="#F83333", underline=True),
#     "tag": Style(color="#ff79c6"),
#     "yaml.field": Style(color="#ff79c6", bold=True),
#     "json.label": Style(color="#ff79c6", bold=True),
#     "toml.type": Style(color="#ff79c6"),
#     "toml.datetime": Style(color="#bd93f9"),
#     "toml.error": _NULL_STYLE,
#     "heading": Style(color="#ff79c6", bold=True),
#     "bold": Style(bold=True),
#     "italic": Style(italic=True),
#     "strikethrough": Style(strike=True),
#     "link": Style(color="#bd93f9", underline=True),
#     "inline_code": Style(color="#ff79c6"),
# }

_BUILTIN_THEMES = {
    "monokai": _MONOKAI,
    # "dracula": _DRACULA,
}


DEFAULT_SYNTAX_THEME = TextAreaTheme.get_theme("monokai")
"""The default syntax highlighting theme used by Textual."""
