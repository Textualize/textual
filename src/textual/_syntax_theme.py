from __future__ import annotations

from dataclasses import dataclass, field

from rich.style import Style

_MONOKAI = {
    "string": Style(color="#E6DB74"),
    "string.documentation": Style(color="yellow"),
    "comment": Style(color="#75715E"),
    "keyword": Style(color="#F92672"),
    "include": Style(color="#F92672"),
    "keyword.function": Style(color="#F92672"),
    "keyword.return": Style(color="#F92672"),
    "conditional": Style(color="#F92672"),
    "number": Style(color="#AE81FF"),
    "class": Style(color="#A6E22E"),
    "function": Style(color="#A6E22E"),
    "function.call": Style(color="#A6E22E"),
    "method": Style(color="#A6E22E"),
    "method.call": Style(color="#A6E22E"),
    # "constant": Style(color="#AE81FF"),
    "variable": Style(color="white"),
    "parameter": Style(color="cyan"),
    # "type": Style(color="cyan"),
    "escape": Style(bgcolor="magenta"),
    "heading": Style(color="#F92672", bold=True),
}

BUILTIN_THEMES = {
    "monokai": _MONOKAI,
    "bluokai": {**_MONOKAI, "string": Style.parse("cyan")},
}


NULL_STYLE = Style.null()


@dataclass
class SyntaxTheme:
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

    style_mapping: dict[str, Style] = field(default_factory=dict)
    """The mapping of names from the `highlight_query` to Rich styles."""

    highlight_query: str = ""
    """The tree-sitter query to use for highlighting.

    See `*.scm` files in this repo for examples, as well as the tree-sitter docs.

    Note that the `highlight_query` must only refer to nodes which are defined in the
    tree-sitter language/parser currently being used. If the query refers to nodes
    that the parser does not declare, tree-sitter will raise an exception.
    """

    @classmethod
    def get_theme(cls, theme_name: str) -> "SyntaxTheme":
        return cls(theme_name, BUILTIN_THEMES.get(theme_name, {}))

    def get_highlight(self, name: str) -> Style:
        return self.style_mapping.get(name, NULL_STYLE)

    @classmethod
    def available_themes(cls) -> list[SyntaxTheme]:
        return [SyntaxTheme(name, mapping) for name, mapping in BUILTIN_THEMES.items()]


DEFAULT_SYNTAX_THEME = SyntaxTheme.get_theme("monokai")
