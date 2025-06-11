"""
Utilities related to content markup.

"""

from __future__ import annotations

from operator import itemgetter

from textual.css.parse import substitute_references
from textual.css.tokenizer import UnexpectedEnd

__all__ = ["MarkupError", "escape", "to_content"]

import re
from string import Template
from typing import TYPE_CHECKING, Callable, Mapping, Match

from textual._context import active_app
from textual.color import Color
from textual.css.tokenize import (
    COLOR,
    PERCENT,
    TOKEN,
    VARIABLE_REF,
    Expect,
    TokenizerState,
    tokenize_values,
)
from textual.style import Style

if TYPE_CHECKING:
    from textual.content import Content


class MarkupError(Exception):
    """An error occurred parsing content markup."""


expect_markup_tag = (
    Expect(
        "markup style value",
        end_tag=r"(?<!\\)\]",
        key=r"[@a-zA-Z_-][a-zA-Z0-9_-]*=",
        percent=PERCENT,
        color=COLOR,
        token=TOKEN,
        variable_ref=VARIABLE_REF,
        whitespace=r"\s+",
    )
    .expect_eof(True)
    .expect_semicolon(False)
    .extract_text(True)
)

expect_markup = Expect(
    "markup tag",
    open_closing_tag=r"(?<!\\)\[/",
    open_tag=r"(?<!\\)\[",
).extract_text()

expect_markup_expression = (
    Expect(
        "markup value",
        end_tag=r"(?<!\\)\]",
        word=r"[\w\.]+",
        round_start=r"\(",
        round_end=r"\)",
        square_start=r"\[",
        square_end=r"\]",
        curly_start=r"\{",
        curly_end=r"\}",
        comma=",",
        whitespace=r"\s+",
        double_string=r"\".*?\"",
        single_string=r"'.*?'",
    )
    .expect_eof(True)
    .expect_semicolon(False)
)


class MarkupTokenizer(TokenizerState):
    """Tokenizes content markup."""

    EXPECT = expect_markup.expect_eof()
    STATE_MAP = {
        "open_tag": expect_markup_tag,
        "open_closing_tag": expect_markup_tag,
        "end_tag": expect_markup,
        "key": expect_markup_expression,
    }
    STATE_PUSH = {
        "round_start": expect_markup_expression,
        "square_start": expect_markup_expression,
        "curly_start": expect_markup_expression,
    }
    STATE_POP = {
        "round_end": "round_start",
        "square_end": "square_start",
        "curly_end": "curly_start",
    }


expect_style = Expect(
    "style token",
    end_tag=r"(?<!\\)\]",
    key=r"[@a-zA-Z_-][a-zA-Z0-9_-]*=",
    percent=PERCENT,
    color=COLOR,
    token=TOKEN,
    variable_ref=VARIABLE_REF,
    whitespace=r"\s+",
    double_string=r"\".*?\"",
    single_string=r"'.*?'",
).expect_semicolon(False)


class StyleTokenizer(TokenizerState):
    """Tokenizes a style"""

    EXPECT = expect_style.expect_eof()
    STATE_MAP = {"key": expect_markup_expression}
    STATE_PUSH = {
        "round_start": expect_markup_expression,
        "square_start": expect_markup_expression,
        "curly_start": expect_markup_expression,
    }


STYLES = {
    "bold",
    "dim",
    "italic",
    "underline",
    "underline2",
    "reverse",
    "strike",
    "blink",
}
STYLE_ABBREVIATIONS = {
    "b": "bold",
    "d": "dim",
    "i": "italic",
    "u": "underline",
    "uu": "underline2",
    "r": "reverse",
    "s": "strike",
}

_ReStringMatch = Match[str]  # regex match object
_ReSubCallable = Callable[[_ReStringMatch], str]  # Callable invoked by re.sub
_EscapeSubMethod = Callable[[_ReSubCallable, str], str]  # Sub method of a compiled re


def escape(
    markup: str,
    _escape: _EscapeSubMethod = re.compile(r"(\\*)(\[[a-z#/@][^[]*?])").sub,
) -> str:
    """Escapes text so that it won't be interpreted as markup.

    Args:
        markup (str): Content to be inserted in to markup.

    Returns:
        str: Markup with square brackets escaped.
    """

    def escape_backslashes(match: Match[str]) -> str:
        """Called by re.sub replace matches."""
        backslashes, text = match.groups()
        return f"{backslashes}{backslashes}\\{text}"

    markup = _escape(escape_backslashes, markup)
    if markup.endswith("\\") and not markup.endswith("\\\\"):
        return markup + "\\"

    return markup


def parse_style(style: str, variables: dict[str, str] | None = None) -> Style:
    """Parse a style with substituted variables.

    Args:
        style: Style encoded in a string.
        variables: Mapping of variables, or `None` to import from active app.

    Returns:
        A Style object.
    """

    styles: dict[str, bool | None] = {}
    color: Color | None = None
    background: Color | None = None
    is_background: bool = False
    style_state: bool = True

    tokenizer = StyleTokenizer()
    meta = {}

    if variables is None:
        try:
            app = active_app.get()
        except LookupError:
            reference_tokens = {}
        else:
            reference_tokens = app.stylesheet._variable_tokens
    else:
        reference_tokens = tokenize_values(variables)

    iter_tokens = iter(
        substitute_references(
            tokenizer(style, ("inline style", "")),
            reference_tokens,
        )
    )

    for token in iter_tokens:
        token_name = token.name
        token_value = token.value
        if token_name == "key":
            key = token_value.rstrip("=")
            parenthesis: list[str] = []
            value_text: list[str] = []
            first_token = next(iter_tokens)
            if first_token.name in {"double_string", "single_string"}:
                meta[key] = first_token.value[1:-1]
                break
            else:
                value_text.append(first_token.value)
                for token in iter_tokens:
                    if token.name == "whitespace" and not parenthesis:
                        break
                    value_text.append(token.value)
                    if token.name in {"round_start", "square_start", "curly_start"}:
                        parenthesis.append(token.value)
                    elif token.name in {"round_end", "square_end", "curly_end"}:
                        parenthesis.pop()
                        if not parenthesis:
                            break
                tokenizer.expect(StyleTokenizer.EXPECT)

                value = "".join(value_text)
                meta[key] = value

        elif token_name == "color":
            if is_background:
                background = Color.parse(token.value)
            else:
                color = Color.parse(token.value)

        elif token_name == "token":
            if token_value == "link":
                if "link" not in meta:
                    meta["link"] = ""
            elif token_value == "on":
                is_background = True
            elif token_value == "auto":
                if is_background:
                    background = Color.automatic()
                else:
                    color = Color.automatic()
            elif token_value == "not":
                style_state = False
            elif token_value in STYLES:
                styles[token_value] = style_state
                style_state = True
            elif token_value in STYLE_ABBREVIATIONS:
                styles[STYLE_ABBREVIATIONS[token_value]] = style_state
                style_state = True
            else:
                if is_background:
                    background = Color.parse(token_value)
                else:
                    color = Color.parse(token_value)

        elif token_name == "percent":
            percent = int(token_value.rstrip("%")) / 100.0
            if is_background:
                if background is not None:
                    background = background.multiply_alpha(percent)
            else:
                if color is not None:
                    color = color.multiply_alpha(percent)

    parsed_style = Style(background, color, link=meta.pop("link", None), **styles)

    if meta:
        parsed_style += Style.from_meta(meta)
    return parsed_style


def to_content(
    markup: str,
    style: str | Style = "",
    template_variables: Mapping[str, object] | None = None,
) -> Content:
    """Convert markup to Content.

    Args:
        markup: String containing markup.
        style: Optional base style.
        template_variables: Mapping of string.Template variables

    Raises:
        MarkupError: If the markup is invalid.

    Returns:
        Content that renders the markup.
    """
    _rich_traceback_omit = True
    try:
        return _to_content(markup, style, template_variables)
    except UnexpectedEnd:
        raise MarkupError(
            "Unexpected end of markup; are you missing a closing square bracket?"
        ) from None
    except Exception as error:
        # Ensure all errors are wrapped in a MarkupError
        raise MarkupError(str(error)) from None


def _to_content(
    markup: str,
    style: str | Style = "",
    template_variables: Mapping[str, object] | None = None,
) -> Content:
    """Internal function to convert markup to Content.

    Args:
        markup: String containing markup.
        style: Optional base style.
        template_variables: Mapping of string.Template variables

    Raises:
        MarkupError: If the markup is invalid.

    Returns:
        Content that renders the markup.
    """

    from textual.content import Content, Span

    tokenizer = MarkupTokenizer()
    text: list[str] = []
    text_append = text.append
    iter_tokens = iter(tokenizer(markup, ("inline", "")))

    style_stack: list[tuple[int, str, str]] = []

    spans: list[Span] = []

    position = 0
    tag_text: list[str]

    normalize_markup_tag = Style._normalize_markup_tag

    if template_variables is None:
        process_text = lambda text: text

    else:

        def process_text(template_text: str, /) -> str:
            if "$" in template_text:
                return Template(template_text).safe_substitute(template_variables)
            return template_text

    for token in iter_tokens:
        token_name = token.name
        if token_name == "text":
            value = process_text(token.value.replace("\\[", "["))
            text_append(value)
            position += len(value)

        elif token_name == "open_tag":
            tag_text = []

            eof = False
            contains_text = False
            for token in iter_tokens:
                if token.name == "end_tag":
                    break
                elif token.name == "text":
                    contains_text = True
                elif token.name == "eof":
                    eof = True
                tag_text.append(token.value)
            if contains_text or eof:
                # "tag" was unparsable
                text_content = f"[{''.join(tag_text)}" + ("" if eof else "]")
                text_append(text_content)
                position += len(text_content)
            else:
                opening_tag = "".join(tag_text)

                if not opening_tag.strip():
                    blank_tag = f"[{opening_tag}]"
                    text_append(blank_tag)
                    position += len(blank_tag)
                else:
                    style_stack.append(
                        (
                            position,
                            opening_tag,
                            normalize_markup_tag(opening_tag.strip()),
                        )
                    )

        elif token_name == "open_closing_tag":
            tag_text = []
            for token in iter_tokens:
                if token.name == "end_tag":
                    break
                tag_text.append(token.value)
            closing_tag = "".join(tag_text).strip()
            normalized_closing_tag = normalize_markup_tag(closing_tag)
            if normalized_closing_tag:
                for index, (tag_position, tag_body, normalized_tag_body) in enumerate(
                    reversed(style_stack), 1
                ):
                    if normalized_tag_body == normalized_closing_tag:
                        style_stack.pop(-index)
                        if tag_position != position:
                            spans.append(Span(tag_position, position, tag_body))
                        break
                else:
                    raise MarkupError(
                        f"closing tag '[/{closing_tag}]' does not match any open tag"
                    )

            else:
                if not style_stack:
                    raise MarkupError("auto closing tag ('[/]') has nothing to close")
                open_position, tag_body, _ = style_stack.pop()
                if open_position != position:
                    spans.append(Span(open_position, position, tag_body))

    content_text = "".join(text)
    text_length = len(content_text)
    if style_stack and text_length:
        spans.extend(
            [
                Span(position, text_length, tag_body)
                for position, tag_body, _ in reversed(style_stack)
                if position != text_length
            ]
        )
    spans.reverse()
    spans.sort(key=itemgetter(0))  # Zeroth item of Span is 'start' attribute

    content = Content(
        content_text,
        [Span(0, text_length, style), *spans] if (style and text_length) else spans,
    )

    return content


if __name__ == "__main__":  # pragma: no cover
    from textual._markup_playground import MarkupPlayground

    app = MarkupPlayground()
    app.run()
