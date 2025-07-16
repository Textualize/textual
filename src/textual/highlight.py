from __future__ import annotations

from pygments.lexers import get_lexer_by_name
from pygments.token import Token

from textual.content import Content, Span

TokenType = tuple[str, ...]


class HighlightTheme:

    STYLES: dict[TokenType, str] = {
        # Generic.Deleted: Style(color="bright_red"),
        # Generic.Heading: Style(bold=True),
        # Generic.Inserted: Style(color="green"),
        # Generic.Prompt: Style(bold=True),
        # Generic.Subheading: Style(color="magenta", bold=True),
        # Name.Attribute: Style(color="cyan"),
        # Name.Builtin: Style(color="cyan"),
        # Name.Class: Style(color="green", underline=True),
        # Name.Exception: Style(color="cyan"),
        # Name.Function: Style(color="green"),
        # Name.Namespace: Style(color="cyan", underline=True),
        # Token: "$text",
        # Token.Comment.Double: "green",
        # Token.Comment.Preproc: "$success",
        Token.Comment: "$text 60%",
        Token.Error: "$error on $error-muted",
        Token.Generic.Error: "$error on $error-muted",
        Token.Keyword: "$accent",
        Token.Keyword.Constant: "bold $success 80%",
        Token.Keyword.Namespace: "$error",
        Token.Keyword.Type: "bold",
        Token.Literal.Number.Integer: "$warning",
        Token.Literal.String: "$success 90%",
        Token.Literal.String.Doc: "$success 80% italic",
        Token.Literal.String.Double: "$success 90%",
        Token.Name: "$primary",
        Token.Name.Builtin: "$accent",
        Token.Name.Builtin.Pseudo: "italic",
        Token.Name.Class: "$warning bold",
        Token.Name.Constant: "$error",
        Token.Name.Decorator: "$primary bold",
        Token.Name.Function: "$warning underline",
        Token.Name.Function.Magic: "$warning underline",
        Token.Name.Tag: "$primary",
        Token.Name.Variable: "$secondary",
        Token.Number: "$secondary",
        Token.Operator: "bold",
        Token.Operator.Word: "bold",
        Token.String: "$success",
        Token.Whitespace: "",
    }


def highlight(
    code: str,
    language: str = "text",
    theme: type[HighlightTheme] = HighlightTheme,
    tab_size: int = 8,
) -> Content:
    code = "\n".join(code.splitlines())
    lexer = get_lexer_by_name(
        language,
        stripnl=False,
        ensurenl=True,
        tabsize=tab_size,
    )
    token_start = 0
    spans: list[Span] = []
    styles = theme.STYLES

    for token_type, token in lexer.get_tokens(code):
        token_end = token_start + len(token)
        while True:
            if style := styles.get(token_type):
                spans.append(Span(token_start, token_end, style))
                break
            else:
                if (token_type := token_type.parent) is None:
                    break
        token_start = token_end

    highlighted_code = Content(code, spans=spans).stylize_before("$text")
    return highlighted_code


if __name__ == "__main__":

    CODE = '''
from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")

# This is a comment

class PygmentsSyntaxTheme(SyntaxTheme):
    """Syntax theme that delegates to Pygments theme."""

    def __init__(self, theme: Union[str, Type[PygmentsStyle]]) -> None:
        self._style_cache: Dict[TokenType, Style] = {}
        if isinstance(theme, str):
            try:
                self._pygments_style_class = get_style_by_name(theme)
            except ClassNotFound:
                self._pygments_style_class = get_style_by_name("default")
        else:
            self._pygments_style_class = theme

        self._background_color = self._pygments_style_class.background_color
        self._background_style = Style(bgcolor=self._background_color)



def loop_first(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    yield True, value
    for value in iter_values:
        yield False, value

def loop_last(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    for value in iter_values:
        yield False, previous_value
        previous_value = value
    yield True, previous_value


def loop_first_last(values: Iterable[T]) -> Iterable[Tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value
'''
    lexer = get_lexer_by_name(
        "python",
        stripnl=False,
        ensurenl=True,
        tabsize=8,
    )
    for token_type, token in lexer.get_tokens(CODE):
        print(f"{token_type}, {token[:20]!r}")

    # highlight(CODE, "python")

    spans = [
        Span(0, 49, style="$text"),
    ]

    c = Content("--- hello.py\t2024-01-15 10:30:00.000000000 -0800", spans=spans)
    from textual.style import Style

    c.render_strips({}, 80, None, Style())
