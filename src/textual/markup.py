from __future__ import annotations

__all__ = ["MarkupError", "escape", "to_content"]

import re
from ast import literal_eval
from operator import attrgetter
from typing import (
    TYPE_CHECKING,
    Callable,
    Iterable,
    List,
    Match,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

from textual.css.tokenize import (
    COLOR,
    PERCENT,
    TOKEN,
    VARIABLE_REF,
    Expect,
    TokenizerState,
)
from textual.style import Style

if TYPE_CHECKING:
    from textual.content import Content


class MarkupError(Exception):
    """An error occurred parsing Textual markup."""


expect_markup_tag = Expect(
    "style token",
    end_tag=r"(?<!\\)\]",
    key=r"[@a-zA-Z_-][a-zA-Z0-9_-]*=",
    percent=PERCENT,
    color=COLOR,
    token=TOKEN,
    variable_ref=VARIABLE_REF,
    whitespace=r"\s+",
)

expect_markup = Expect(
    "markup token",
    open_closing_tag=r"(?<!\\)\[/",
    open_tag=r"(?<!\\)\[",
    end_tag=r"(?<!\\)\]",
).extract_text()

expect_markup_expression = Expect(
    "markup",
    end_tag=r"(?<!\\)\]",
    word=r"\w+",
    period=r"\.",
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


class MarkupTokenizer(TokenizerState):
    """Tokenizes Textual markup."""

    EXPECT = expect_markup.expect_eof(True)
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


RE_TAGS = re.compile(
    r"""((\\*)\[([\$a-z#/@][^[]*?)])""",
    re.VERBOSE,
)

RE_HANDLER = re.compile(r"^([\w.]*?)(\(.*?\))?$")


class Tag(NamedTuple):
    """A tag in console markup."""

    name: str
    """The tag name. e.g. 'bold'."""
    parameters: Optional[str]
    """Any additional parameters after the name."""

    def __str__(self) -> str:
        return (
            self.name if self.parameters is None else f"{self.name} {self.parameters}"
        )

    @property
    def markup(self) -> str:
        """Get the string representation of this tag."""
        return (
            f"[{self.name}]"
            if self.parameters is None
            else f"[{self.name}={self.parameters}]"
        )


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


def _parse(markup: str) -> Iterable[Tuple[int, Optional[str], Optional[Tag]]]:
    """Parse markup in to an iterable of tuples of (position, text, tag).

    Args:
        markup (str): A string containing console markup

    """
    position = 0
    _divmod = divmod
    _Tag = Tag
    for match in RE_TAGS.finditer(markup):
        full_text, escapes, tag_text = match.groups()
        start, end = match.span()
        if start > position:
            yield start, markup[position:start], None
        if escapes:
            backslashes, escaped = _divmod(len(escapes), 2)
            if backslashes:
                # Literal backslashes
                yield start, "\\" * backslashes, None
                start += backslashes * 2
            if escaped:
                # Escape of tag
                yield start, full_text[len(escapes) :], None
                position = end
                continue
        text, equals, parameters = tag_text.partition("=")
        yield start, None, _Tag(text, parameters if equals else None)
        position = end
    if position < len(markup):
        yield position, markup[position:], None


def to_content(
    markup: str,
    style: Union[str, Style] = "",
) -> Content:
    """Render console markup in to a Text instance.

    Args:
        markup (str): A string containing console markup.
        style: (Union[str, Style]): Base style for entire content, or empty string for no base style.

    Raises:
        MarkupError: If there is a syntax error in the markup.

    Returns:
        Text: A test instance.
    """
    _rich_traceback_omit = True

    from textual.content import Content, Span

    if "[" not in markup:
        return Content(markup)

    text: list[str] = []
    append = text.append
    text_length = 0

    style_stack: List[Tuple[int, Tag]] = []
    pop = style_stack.pop

    spans: List[Span] = []
    append_span = spans.append

    _Span = Span
    _Tag = Tag

    def pop_style(style_name: str) -> Tuple[int, Tag]:
        """Pop tag matching given style name."""
        for index, (_, tag) in enumerate(reversed(style_stack), 1):
            if tag.name == style_name:
                return pop(-index)
        raise KeyError(style_name)

    for position, plain_text, tag in _parse(markup):
        if plain_text is not None:
            # Handle open brace escapes, where the brace is not part of a tag.
            plain_text = plain_text.replace("\\[", "[")
            append(plain_text)
            text_length += len(plain_text)
        elif tag is not None:
            if tag.name.startswith("/"):  # Closing tag
                style_name = tag.name[1:].strip()

                if style_name:  # explicit close
                    try:
                        start, open_tag = pop_style(style_name)
                    except KeyError:
                        raise MarkupError(
                            f"closing tag '{tag.markup}' at position {position} doesn't match any open tag"
                        ) from None
                else:  # implicit close
                    try:
                        start, open_tag = pop()
                    except IndexError:
                        raise MarkupError(
                            f"closing tag '[/]' at position {position} has nothing to close"
                        ) from None

                if open_tag.name.startswith("@"):
                    if open_tag.parameters:
                        handler_name = ""
                        parameters = open_tag.parameters.strip()
                        handler_match = RE_HANDLER.match(parameters)
                        if handler_match is not None:
                            handler_name, match_parameters = handler_match.groups()
                            parameters = (
                                "()" if match_parameters is None else match_parameters
                            )

                        try:
                            meta_params = literal_eval(parameters)
                        except SyntaxError as error:
                            raise MarkupError(
                                f"error parsing {parameters!r} in {open_tag.parameters!r}; {error.msg}"
                            )
                        except Exception as error:
                            raise MarkupError(
                                f"error parsing {open_tag.parameters!r}; {error}"
                            ) from None

                        if handler_name:
                            meta_params = (
                                handler_name,
                                (
                                    meta_params
                                    if isinstance(meta_params, tuple)
                                    else (meta_params,)
                                ),
                            )

                    else:
                        meta_params = ()

                    append_span(
                        _Span(
                            start,
                            text_length,
                            Style.from_meta({open_tag.name: meta_params}),
                        )
                    )
                else:
                    append_span(_Span(start, text_length, str(open_tag)))

            else:  # Opening tag
                normalized_tag = _Tag(tag.name, tag.parameters)
                style_stack.append((text_length, normalized_tag))

    while style_stack:
        start, tag = style_stack.pop()
        style = str(tag)
        if style:
            append_span(_Span(start, text_length, style))

    content = Content("".join(text), sorted(spans[::-1], key=attrgetter("start")))
    return content


def to_content(markup: str, style: str | Style = "") -> Content:

    from textual.content import Content, Span

    tokenizer = MarkupTokenizer()
    text: list[str] = []
    iter_tokens = iter(tokenizer(markup, ("inline", "")))

    style_stack: list[tuple[int, str]] = []

    spans: list[Span] = []

    position = 0
    tag_text: list[str]
    for token in iter_tokens:
        print(repr(token))
        token_name = token.name
        if token_name == "text":
            text.append(token.value)
            position += len(token.value)
        elif token_name == "open_tag":
            tag_text = []
            print("open")
            for token in iter_tokens:
                print("  ", repr(token))
                if token.name == "end_tag":
                    break
                tag_text.append(token.value)
            opening_tag = "".join(tag_text)
            style_stack.append((position, opening_tag))

        elif token_name == "open_closing_tag":
            tag_text = []
            print("closing")
            for token in iter_tokens:
                print("  ", repr(token))
                if token.name == "end_tag":
                    break
                tag_text.append(token.value)
            closing_tag = "".join(tag_text)
            if closing_tag:
                for index, (tag_position, tag_body) in enumerate(reversed(style_stack)):
                    if tag_body == closing_tag:
                        style_stack.pop(-index)
                        spans.append(Span(tag_position, position, tag_body))
                        break

            else:
                open_position, tag = style_stack.pop()
                spans.append(Span(open_position, position, tag))

    content_text = "".join(text)
    text_length = len(content_text)
    while style_stack:
        position, tag = style_stack.pop()
        spans.append(Span(position, text_length, tag))

    content = Content(content_text, spans)
    print(repr(content))
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

            with (container := containers.VerticalScroll(id="results-container")):
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
