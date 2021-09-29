from __future__ import annotations

from typing import NamedTuple
import re

from rich import print
import rich.repr


class EOFError(Exception):
    pass


class TokenizeError(Exception):
    def __init__(self, col_no: int, row_no: int, message: str) -> None:
        self.col_no = col_no
        self.row_no = row_no
        super().__init__(message)


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

    def __rich_repr__(self) -> rich.repr.Result:
        yield from zip(self.names, self.regexes)


class Token(NamedTuple):
    line: int
    col: int
    name: str
    value: str


class Tokenizer:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines(keepends=True)
        self.line_no = 0
        self.col_no = 0

    def get_token(self, expect: Expect) -> Token:
        line_no = self.line_no
        if line_no >= len(self.lines):
            raise EOFError()
        col_no = self.col_no
        line = self.lines[line_no]
        match = expect.match(line, col_no)
        if match is None:
            raise TokenizeError(
                line_no,
                col_no,
                "expected " + ", ".join(name.upper() for name in expect.names),
            )
        iter_groups = iter(match.groups())
        next(iter_groups)

        for name, value in zip(expect.names, iter_groups):
            if value is not None:
                break

        try:
            return Token(line_no, col_no, name, value)
        finally:
            col_no += len(value)
            if col_no >= len(line):
                line_no += 1
                col_no = 0
            self.line_no = line_no
            self.col_no = col_no

    def skip_to(self, expect: Expect) -> Token:
        line_no = self.line_no
        col_no = self.col_no

        while True:
            if line_no >= len(self.lines):
                raise EOFError()
            line = self.lines[line_no]
            match = expect.search(line, col_no)

            if match is None:
                line_no += 1
                col_no = 0
            else:
                self.line_no = line_no
                self.col_no = match.span(0)[0]
                return self.get_token(expect)
