from __future__ import annotations

from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments.util import ClassNotFound

from textual.content import Content, Span

TokenType = tuple[str, ...]


class HighlightTheme:
    """Contains the style definition for user with the highlight method."""

    STYLES: dict[TokenType, str] = {
        Token.Comment: "$text 60%",
        Token.Error: "$error on $error-muted",
        Token.Generic.Error: "$error on $error-muted",
        Token.Keyword: "$accent",
        Token.Keyword.Constant: "bold $success 80%",
        Token.Keyword.Namespace: "$error",
        Token.Keyword.Type: "bold",
        Token.Literal.Number: "$warning",
        Token.Literal.String: "$success 90%",
        Token.Literal.String.Doc: "$success 80% italic",
        Token.Literal.String.Double: "$success 90%",
        Token.Name: "$primary",
        Token.Name.Attribute: "$warning",
        Token.Name.Builtin: "$accent",
        Token.Name.Builtin.Pseudo: "italic",
        Token.Name.Class: "$warning bold",
        Token.Name.Constant: "$error",
        Token.Name.Decorator: "$primary bold",
        Token.Name.Function: "$warning underline",
        Token.Name.Function.Magic: "$warning underline",
        Token.Name.Tag: "$primary bold",
        Token.Name.Variable: "$secondary",
        Token.Number: "$warning",
        Token.Operator: "bold",
        Token.Operator.Word: "bold $error",
        Token.String: "$success",
        Token.Whitespace: "",
    }


def highlight(
    code: str,
    language: str = "text",
    *,
    theme: type[HighlightTheme] = HighlightTheme,
    tab_size: int = 8,
) -> Content:
    """Apply syntax highlighting to a string.

    Args:
        code: A string to highlight.
        language: The language to highlight.
        theme: A HighlightTheme class (type not instance).
        tab_size: Number of spaces in a tab. Defaults to 8.

    Returns:
        A Content instance which may be used in a widget.
    """
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
            else:
                if (token_type := token_type.parent) is None:
                    break
        token_start = token_end

    highlighted_code = Content(code, spans=spans).stylize_before("$text")
    return highlighted_code
