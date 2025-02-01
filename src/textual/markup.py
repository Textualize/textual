from __future__ import annotations

from textual.css.parse import substitute_references

__all__ = ["MarkupError", "escape", "to_content"]

import re
from typing import TYPE_CHECKING, Callable, Match

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
    """An error occurred parsing Textual markup."""


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
    .expect_eof()
    .expect_semicolon(False)
)

expect_markup = Expect(
    "markup tag",
    open_closing_tag=r"(?<!\\)\[/",
    open_tag=r"(?<!\\)\[",
    end_tag=r"(?<!\\)\]",
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
    .expect_eof()
    .expect_semicolon(False)
)


class MarkupTokenizer(TokenizerState):
    """Tokenizes Textual markup."""

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


STYLES = {"bold", "dim", "italic", "underline", "reverse", "strike"}
STYLE_ABBREVIATIONS = {
    "b": "bold",
    "d": "dim",
    "i": "italic",
    "u": "underline",
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
            if token_value == "on":
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

    parsed_style = Style(background, color, link=meta.get("link", None), **styles)

    if meta:
        parsed_style += Style.from_meta(meta)
    return parsed_style


def to_content(markup: str, style: str | Style = "") -> Content:
    _rich_traceback_omit = True
    try:
        return _to_content(markup, style)
    except Exception as error:
        raise MarkupError(str(error)) from None


def _to_content(markup: str, style: str | Style = "") -> Content:

    from textual.content import Content, Span

    tokenizer = MarkupTokenizer()
    text: list[str] = []
    iter_tokens = iter(tokenizer(markup, ("inline", "")))

    style_stack: list[tuple[int, str]] = []

    spans: list[Span] = []

    position = 0
    tag_text: list[str]
    for token in iter_tokens:

        token_name = token.name
        if token_name == "text":
            text.append(token.value)
            position += len(token.value)

        elif token_name == "open_tag":
            tag_text = []
            for token in iter_tokens:
                if token.name == "end_tag":
                    break
                tag_text.append(token.value)
            opening_tag = "".join(tag_text).strip()
            style_stack.append((position, opening_tag))

        elif token_name == "open_closing_tag":
            tag_text = []
            for token in iter_tokens:
                if token.name == "end_tag":
                    break
                tag_text.append(token.value)
            closing_tag = "".join(tag_text).strip()
            if closing_tag:
                for index, (tag_position, tag_body) in enumerate(
                    reversed(style_stack), 1
                ):
                    if tag_body == closing_tag:
                        style_stack.pop(-index)
                        spans.append(Span(tag_position, position, tag_body))
                        break
                else:
                    raise MarkupError(
                        f"closing tag '[/{tag_body}]' does not match any open tag"
                    )

            else:
                if not style_stack:
                    raise MarkupError("auto closing tag ('[/]') has nothing to close")
                open_position, tag = style_stack.pop()
                spans.append(Span(open_position, position, tag))

    content_text = "".join(text)
    text_length = len(content_text)
    while style_stack:
        position, tag = style_stack.pop()
        spans.append(Span(position, text_length, tag))

    if style:
        content = Content(content_text, [Span(0, len(content_text), style), *spans])
    else:
        content = Content(content_text, spans)

    return content


if __name__ == "__main__":  # pragma: no cover
    from rich.highlighter import ReprHighlighter

    from textual import containers, on
    from textual.app import App, ComposeResult
    from textual.widgets import Static, TextArea

    class MarkupApp(App):

        CSS = """
        Screen {
            layout: horizontal;
            #editor {
                width: 1fr;
                border: tab $primary;  
                padding: 1;
                margin: 1 1 0 1;
            }
            #results-container {
                margin: 1 1 0 1;
                border: tab $success;                
                &.-error {
                    border: tab $error;
                }
            }
            #results {
                width: 1fr;
                padding: 1 1;
                
            }
        }
        """

        def compose(self) -> ComposeResult:
            yield (text_area := TextArea(id="editor"))
            text_area.border_title = "Markup"

            with containers.VerticalScroll(id="results-container") as container:
                yield Static(id="results")
            container.border_title = "Output"

        @on(TextArea.Changed)
        def on_markup_changed(self, event: TextArea.Changed) -> None:
            results = self.query_one("#results", Static)
            try:
                results.update(event.text_area.text)
            except Exception as error:
                highlight = ReprHighlighter()
                # results.update(highlight(str(error)))
                from rich.traceback import Traceback

                results.update(Traceback())
                self.query_one("#results-container").add_class("-error")
            else:
                self.query_one("#results-container").remove_class("-error")

    app = MarkupApp()
    app.run()
