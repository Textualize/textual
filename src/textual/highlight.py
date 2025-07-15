from __future__ import annotations

from pygments.lexers import get_lexer_by_name
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    Whitespace,
)

from textual.content import Content, Span

TokenType = tuple[str, ...]

THEME: dict[TokenType, str] = {
    Token: "",
    Whitespace: "",
    Comment: "green",
    Comment.Preproc: "$success",
    Keyword: "$accent bold",
    Token.Literal.String.Doc: "$success 50% italic",
    Token.Operator: "bold",
    Token.Name: "$primary",
    Keyword.Type: "bold",
    Operator.Word: "bold",
    Token.Keyword.Constant: "bold $success 80%",
    # Name.Builtin: Style(color="cyan"),
    # Name.Function: Style(color="green"),
    # Name.Namespace: Style(color="cyan", underline=True),
    # Name.Class: Style(color="green", underline=True),
    # Name.Exception: Style(color="cyan"),
    Name.Decorator: "$primary bold",
    Name.Variable: "$secondary",
    Name.Constant: "$error",
    # Name.Attribute: Style(color="cyan"),
    # Name.Tag: Style(color="bright_blue"),
    String: "$success",
    Number: "$secondary",
    Token.Literal.Number.Integer: "$warning",
    # Generic.Deleted: Style(color="bright_red"),
    # Generic.Inserted: Style(color="green"),
    # Generic.Heading: Style(bold=True),
    # Generic.Subheading: Style(color="magenta", bold=True),
    # Generic.Prompt: Style(bold=True),
    # Generic.Error: Style(color="bright_red"),
    # Error: Style(color="red", underline=True),
}


def highlight(code: str, language: str) -> Content:
    lexer = get_lexer_by_name(
        language,
        stripnl=False,
        ensurenl=True,
        tabsize=8,
    )
    token_start = 0
    spans: list[Span] = []
    for token_type, token in lexer.get_tokens(code):
        token_end = token_start + len(token)
        if style := THEME.get(token_type, None):
            spans.append(Span(token_start, token_end, style))
        token_start = token_end
    highlighted_code = Content(code, spans=spans)
    return highlighted_code


if __name__ == "__main__":

    CODE = '''\
from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")


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

    highlight(CODE, "python")
