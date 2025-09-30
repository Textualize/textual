from __future__ import annotations

import os
from typing import Tuple

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound

from textual.content import Content, Span

TokenType = Tuple[str, ...]


class HighlightTheme:
    """Contains the style definition for user with the highlight method."""

    STYLES: dict[TokenType, str] = {
        Token.Comment: "$text 60%",
        Token.Error: "$text-error on $error-muted",
        Token.Generic.Strong: "bold",
        Token.Generic.Emph: "italic",
        Token.Generic.Error: "$text-error on $error-muted",
        Token.Generic.Heading: "$text-primary underline",
        Token.Generic.Subheading: "$text-primary",
        Token.Keyword: "$text-accent",
        Token.Keyword.Constant: "bold $text-success 80%",
        Token.Keyword.Namespace: "$text-error",
        Token.Keyword.Type: "bold",
        Token.Literal.Number: "$text-warning",
        Token.Literal.String.Backtick: "$text 60%",
        Token.Literal.String: "$text-success 90%",
        Token.Literal.String.Doc: "$text-success 80% italic",
        Token.Literal.String.Double: "$text-success 90%",
        Token.Name: "$text-primary",
        Token.Name.Attribute: "$text-warning",
        Token.Name.Builtin: "$text-accent",
        Token.Name.Builtin.Pseudo: "italic",
        Token.Name.Class: "$text-warning bold",
        Token.Name.Constant: "$text-error",
        Token.Name.Decorator: "$text-primary bold",
        Token.Name.Function: "$text-warning underline",
        Token.Name.Function.Magic: "$text-warning underline",
        Token.Name.Tag: "$text-primary bold",
        Token.Name.Variable: "$text-secondary",
        Token.Number: "$text-warning",
        Token.Operator: "bold",
        Token.Operator.Word: "bold $text-error",
        Token.String: "$text-success",
        Token.Whitespace: "",
    }


def guess_language(code: str, path: str) -> str:
    """Guess the language based on the code and path.
    The result may be used in the [highlight][textual.highlight.highlight] function.

    Args:
        code: The code to guess from.
        path: A path to the code.

    Returns:
        The language, suitable for use with Pygments.
    """

    if path is not None and os.path.splitext(path)[-1] == ".tcss":
        # A special case for TCSS files which aren't known outside of Textual
        return "scss"

    lexer: Lexer | None = None
    lexer_name = "default"
    if code:
        try:
            lexer = guess_lexer_for_filename(path, code)
        except ClassNotFound:
            pass

    if not lexer:
        try:
            _, ext = os.path.splitext(path)
            if ext:
                extension = ext.lstrip(".").lower()
                lexer = get_lexer_by_name(extension)
        except ClassNotFound:
            pass

    if lexer:
        if lexer.aliases:
            lexer_name = lexer.aliases[0]
        else:
            lexer_name = lexer.name

    return lexer_name


def highlight(
    code: str,
    *,
    language: str | None = None,
    path: str | None = None,
    theme: type[HighlightTheme] = HighlightTheme,
    tab_size: int = 8,
) -> Content:
    """Apply syntax highlighting to a string.

    Args:
        code: A string to highlight.
        language: The language to highlight.
        theme: A HighlightTheme class (type not instance).
        tab_size: Number of spaces in a tab.

    Returns:
        A Content instance which may be used in a widget.
    """
    if language is None:
        if path is None:
            raise RuntimeError("One of 'language' or 'path' must be supplied.")
        language = guess_language(code, path)

    assert language is not None
    code = "\n".join(code.splitlines())
    try:
        lexer = get_lexer_by_name(
            language,
            stripnl=False,
            ensurenl=True,
            tabsize=tab_size,
        )
    except ClassNotFound:
        lexer = get_lexer_by_name(
            "text",
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
            if (token_type := token_type.parent) is None:
                break
        token_start = token_end

    highlighted_code = Content(code, spans=spans).stylize_before("$text")
    return highlighted_code
