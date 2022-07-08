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

from .._loop import loop_last


class TokenizeError(Exception):
    """Error raised when the CSS cannot be tokenized (syntax error)."""

    def __init__(
        self, path: str, code: str, line_no: int, col_no: int, message: str
    ) -> None:
        """
        Args:
            path (str): Path to source or "<object>" if source is parsed from a literal.
            code (str): The code being parsed.
            line_no (int): Line number of the error.
            col_no (int): Column number of the error.
            message (str): A message associated with the error.
        """
        self.path = path
        self.code = code
        self.line_no = line_no
        self.col_no = col_no
        super().__init__(message)

    @classmethod
    def _get_snippet(cls, code: str, line_no: int) -> Panel:
        """Get a short snippet of code around a given line number.

        Args:
            code (str): The code.
            line_no (int): Line number.

        Returns:
            Panel: A renderable.
        """
        # TODO: Highlight column number
        syntax = Syntax(
            code,
            lexer="scss",
            theme="ansi_light",
            line_numbers=True,
            indent_guides=True,
            line_range=(max(0, line_no - 2), line_no + 2),
            highlight_lines={line_no},
        )
        return Panel(syntax, border_style="red")

    def __rich__(self) -> RenderableType:
        highlighter = ReprHighlighter()
        errors: list[RenderableType] = []

        message = str(self)
        errors.append(Text(" Tokenizer error in stylesheet:", style="bold red"))

        errors.append(
            highlighter(
                f" {self.path or '<unknown>'}:{self.line_no + 1}:{self.col_no + 1}"
            )
        )
        errors.append(self._get_snippet(self.code, self.line_no + 1))
        final_message = ""
        for is_last, message_part in loop_last(message.split(";")):
            end = "" if is_last else "\n"
            final_message += f"• {message_part.strip()};{end}"
        errors.append(Padding(highlighter(Text(final_message, "red")), pad=(0, 1)))

        return Group(*errors)


class EOFError(TokenizeError):
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


@rich.repr.auto
class Token(NamedTuple):
    name: str
    value: str
    path: str
    code: str
    location: tuple[int, int]
    referenced_by: ReferencedBy | None = None

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
                return Token("eof", "", self.path, self.code, (line_no, col_no), None)
            else:
                raise EOFError(
                    self.path, self.code, line_no, col_no, "Unexpected end of file"
                )
        line = self.lines[line_no]
        match = expect.match(line, col_no)
        if match is None:
            raise TokenizeError(
                self.path,
                self.code,
                line_no,
                col_no,
                "expected " + ", ".join(name.upper() for name in expect.names),
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
