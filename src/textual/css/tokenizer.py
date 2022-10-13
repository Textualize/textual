from __future__ import annotations

import re
from pathlib import PurePath
from typing import NamedTuple

from rich.console import Group, RenderableType
from rich.highlighter import ReprHighlighter
from rich.padding import Padding
from rich.panel import Panel
import rich.repr
from rich.syntax import Syntax
from rich.text import Text

from ._error_tools import friendly_list


class TokenError(Exception):
    """Error raised when the CSS cannot be tokenized (syntax error)."""

    def __init__(
        self,
        path: str,
        code: str,
        start: tuple[int, int],
        message: str,
        end: tuple[int, int] | None = None,
    ) -> None:
        """
        Args:
            path (str): Path to source or "<object>" if source is parsed from a literal.
            code (str): The code being parsed.
            start (tuple[int, int]): Line number of the error.
            message (str): A message associated with the error.
            end (tuple[int, int] | None): End location of token, or None if not known. Defaults to None.
        """

        self.path = path
        self.code = code
        self.start = start
        self.end = end or start
        super().__init__(message)

    def _get_snippet(self) -> Panel:
        """Get a short snippet of code around a given line number.

        Returns:
            Panel: A renderable.
        """
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
        syntax.stylize_range("reverse bold", self.start, self.end)
        return Panel(syntax, border_style="red")

    def __rich__(self) -> RenderableType:
        highlighter = ReprHighlighter()
        errors: list[RenderableType] = []

        message = str(self)
        errors.append(Text(" Error in stylesheet:", style="bold red"))

        line_no, col_no = self.start

        errors.append(highlighter(f" {self.path or '<unknown>'}:{line_no}:{col_no}"))
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
    pass


class Expect:
    def __init__(self, **tokens: str) -> None:
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


@rich.repr.auto
class Token(NamedTuple):
    name: str
    value: str
    path: str
    code: str
    location: tuple[int, int]
    referenced_by: ReferencedBy | None = None

    @property
    def start(self) -> tuple[int, int]:
        """Start line and column (1 indexed)."""
        line, offset = self.location
        return (line + 1, offset)

    @property
    def end(self) -> tuple[int, int]:
        """End line and column (1 indexed)."""
        line, offset = self.location
        return (line + 1, offset + len(self.value))

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
            path=self.path,
            code=self.code,
            location=self.location,
            referenced_by=by,
        )

    def __str__(self) -> str:
        return self.value

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self.name
        yield "value", self.value
        yield "path", self.path
        yield "code", self.code if len(self.code) < 40 else self.code[:40] + "..."
        yield "location", self.location
        yield "referenced_by", self.referenced_by, None


class Tokenizer:
    def __init__(self, text: str, path: str | PurePath = "") -> None:
        self.path = str(path)
        self.code = text
        self.lines = text.splitlines(keepends=True)
        self.line_no = 0
        self.col_no = 0

    def get_token(self, expect: Expect) -> Token:
        line_no = self.line_no
        col_no = self.col_no
        if line_no >= len(self.lines):
            if expect._expect_eof:
                return Token(
                    "eof",
                    "",
                    self.path,
                    self.code,
                    (line_no + 1, col_no + 1),
                    None,
                )
            else:
                raise EOFError(
                    self.path,
                    self.code,
                    (line_no + 1, col_no + 1),
                    "Unexpected end of file",
                )
        line = self.lines[line_no]
        match = expect.match(line, col_no)
        if match is None:
            expected = friendly_list(" ".join(name.split("_")) for name in expect.names)
            message = f"Expected one of {expected}.; Did you forget a semicolon at the end of a line?"
            raise TokenError(
                self.path,
                self.code,
                (line_no, col_no),
                message,
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
            self.path,
            self.code,
            (line_no, col_no),
            referenced_by=None,
        )
        col_no += len(value)
        if col_no >= len(line):
            line_no += 1
            col_no = 0
        self.line_no = line_no
        self.col_no = col_no
        return token

    def skip_to(self, expect: Expect) -> Token:
        line_no = self.line_no
        col_no = self.col_no

        while True:
            if line_no >= len(self.lines):
                raise EOFError(
                    self.path, self.code, line_no, col_no, "Unexpected end of file"
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
