from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

import rich.repr
from rich.console import Group, RenderableType
from rich.highlighter import ReprHighlighter
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from ..suggestions import get_suggestion
from ._error_tools import friendly_list
from .constants import VALID_PSEUDO_CLASSES

if TYPE_CHECKING:
    from .types import CSSLocation


class TokenError(Exception):
    """Error raised when the CSS cannot be tokenized (syntax error)."""

    def __init__(
        self,
        read_from: CSSLocation,
        code: str,
        start: tuple[int, int],
        message: str,
        end: tuple[int, int] | None = None,
    ) -> None:
        """
        Args:
            read_from: The location where the CSS was read from.
            code: The code being parsed.
            start: Line and column number of the error (1-indexed).
            message: A message associated with the error.
            end: End location of token (1-indexed), or None if not known.
        """

        self.read_from = read_from
        self.code = code
        self.start = start
        self.end = end or start
        super().__init__(message)

    def _get_snippet(self) -> Panel:
        """Get a short snippet of code around a given line number.

        Returns:
            A renderable.
        """
        from rich.syntax import Syntax

        line_no = self.start[0]
        # TODO: Highlight column number
        syntax = Syntax(
            self.code,
            lexer="scss",
            theme="ansi_light",
            line_numbers=True,
            indent_guides=True,
            line_range=(max(0, line_no - 2), line_no + 2),
            highlight_lines={line_no},
        )
        syntax.stylize_range(
            "reverse bold",
            (self.start[0], self.start[1] - 1),
            (self.end[0], self.end[1] - 1),
        )
        return Panel(syntax, border_style="red")

    def __rich__(self) -> RenderableType:
        highlighter = ReprHighlighter()
        errors: list[RenderableType] = []

        message = str(self)
        errors.append(Text(" Error in stylesheet:", style="bold red"))

        line_no, col_no = self.start

        path, widget_variable = self.read_from
        if widget_variable:
            css_location = f" {path}, {widget_variable}:{line_no}:{col_no}"
        else:
            css_location = f" {path}:{line_no}:{col_no}"
        errors.append(highlighter(css_location))
        errors.append(self._get_snippet())

        final_message = "\n".join(
            f"• {message_part.strip()}" for message_part in message.split(";")
        )
        errors.append(
            Padding(
                highlighter(
                    Text(final_message, "red"),
                ),
                pad=(0, 1),
            )
        )

        return Group(*errors)


class EOFError(TokenError):
    """Indicates that the CSS ended prematurely."""


@rich.repr.auto
class Expect:
    """Object that describes the format of tokens."""

    def __init__(self, description: str, **tokens: str) -> None:
        """Create Expect object.

        Args:
            description: Description of this class of tokens, used in errors.
        """
        self.description = f"Expected {description}"
        self.names = list(tokens.keys())
        self.regexes = list(tokens.values())
        self._regex = re.compile(
            "("
            + "|".join(f"(?P<{name}>{regex})" for name, regex in tokens.items())
            + ")"
        )
        self.match = self._regex.match
        self.search = self._regex.search
        self._expect_eof = False

    def expect_eof(self, eof: bool) -> Expect:
        self._expect_eof = eof
        return self

    def __rich_repr__(self) -> rich.repr.Result:
        yield from zip(self.names, self.regexes)


class ReferencedBy(NamedTuple):
    name: str
    location: tuple[int, int]
    length: int
    code: str


@rich.repr.auto(angular=True)
class Token(NamedTuple):
    name: str
    value: str
    read_from: CSSLocation
    code: str
    location: tuple[int, int]
    """Token starting location, 0-indexed."""
    referenced_by: ReferencedBy | None = None

    @property
    def start(self) -> tuple[int, int]:
        """Start line and column (1-indexed)."""
        line, offset = self.location
        return (line + 1, offset + 1)

    @property
    def end(self) -> tuple[int, int]:
        """End line and column (1-indexed)."""
        line, offset = self.location
        return (line + 1, offset + len(self.value) + 1)

    def with_reference(self, by: ReferencedBy | None) -> "Token":
        """Return a copy of the Token, with reference information attached.
        This is used for variable substitution, where a variable reference
        can refer to tokens which were defined elsewhere. With the additional
        ReferencedBy data attached, we can track where the token we are referring
        to is used.
        """
        return Token(
            name=self.name,
            value=self.value,
            read_from=self.read_from,
            code=self.code,
            location=self.location,
            referenced_by=by,
        )

    def __str__(self) -> str:
        return self.value

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self.name
        yield "value", self.value
        yield (
            "read_from",
            self.read_from[0] if not self.read_from[1] else self.read_from,
        )
        yield "code", self.code if len(self.code) < 40 else self.code[:40] + "..."
        yield "location", self.location
        yield "referenced_by", self.referenced_by, None


class Tokenizer:
    """Tokenizes Textual CSS."""

    def __init__(self, text: str, read_from: CSSLocation = ("", "")) -> None:
        """Initialize the tokenizer.

        Args:
            text: String containing CSS.
            read_from: Information regarding where the CSS was read from.
        """
        self.read_from = read_from
        self.code = text
        self.lines = text.splitlines(keepends=True)
        self.line_no = 0
        self.col_no = 0

    def get_token(self, expect: Expect) -> Token:
        """Get the next token.

        Args:
            expect: Expect object which describes which tokens may be read.

        Raises:
            EOFError: If there is an unexpected end of file.
            TokenError: If there is an error with the token.

        Returns:
            A new Token.
        """

        line_no = self.line_no
        col_no = self.col_no
        if line_no >= len(self.lines):
            if expect._expect_eof:
                return Token(
                    "eof",
                    "",
                    self.read_from,
                    self.code,
                    (line_no, col_no),
                    None,
                )
            else:
                raise EOFError(
                    self.read_from,
                    self.code,
                    (line_no + 1, col_no + 1),
                    "Unexpected end of file; did you forget a '}' ?",
                )
        line = self.lines[line_no]
        match = expect.match(line, col_no)
        if match is None:
            error_line = line[col_no:].rstrip()
            error_message = (
                f"{expect.description} (found {error_line.split(';')[0]!r})."
            )
            if not error_line.endswith(";"):
                error_message += "; Did you forget a semicolon at the end of a line?"
            raise TokenError(
                self.read_from, self.code, (line_no + 1, col_no + 1), error_message
            )
        iter_groups = iter(match.groups())

        next(iter_groups)

        for name, value in zip(expect.names, iter_groups):
            if value is not None:
                break
        else:
            # For MyPy's benefit
            raise AssertionError("can't reach here")

        token = Token(
            name,
            value,
            self.read_from,
            self.code,
            (line_no, col_no),
            referenced_by=None,
        )

        if (
            token.name == "pseudo_class"
            and token.value.strip(":") not in VALID_PSEUDO_CLASSES
        ):
            pseudo_class = token.value.strip(":")
            suggestion = get_suggestion(pseudo_class, list(VALID_PSEUDO_CLASSES))
            all_valid = f"must be one of {friendly_list(VALID_PSEUDO_CLASSES)}"
            if suggestion:
                raise TokenError(
                    self.read_from,
                    self.code,
                    (line_no + 1, col_no + 1),
                    f"unknown pseudo-class {pseudo_class!r}; did you mean {suggestion!r}?; {all_valid}",
                )
            else:
                raise TokenError(
                    self.read_from,
                    self.code,
                    (line_no + 1, col_no + 1),
                    f"unknown pseudo-class {pseudo_class!r}; {all_valid}",
                )

        col_no += len(value)
        if col_no >= len(line):
            line_no += 1
            col_no = 0
        self.line_no = line_no
        self.col_no = col_no
        return token

    def skip_to(self, expect: Expect) -> Token:
        """Skip tokens.

        Args:
            expect: Expect object describing the expected token.

        Raises:
            EOFError: If end of file is reached.

        Returns:
            A new token.
        """
        line_no = self.line_no
        col_no = self.col_no

        while True:
            if line_no >= len(self.lines):
                raise EOFError(
                    self.read_from,
                    self.code,
                    (line_no, col_no),
                    "Unexpected end of file; did you forget a '}' ?",
                )
            line = self.lines[line_no]
            match = expect.search(line, col_no)

            if match is None:
                line_no += 1
                col_no = 0
            else:
                self.line_no = line_no
                self.col_no = match.span(0)[0]
                return self.get_token(expect)
