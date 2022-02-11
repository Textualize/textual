from __future__ import annotations

import re
from typing import NamedTuple

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
    referenced_by: ReferencedBy | None

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
        yield "location", self.location
        yield "referenced_by", self.referenced_by


class Tokenizer:
    def __init__(self, text: str, path: str = "") -> None:
        self.path = path
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
                raise EOFError()
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

        token = Token(
            name, value, self.path, self.code, (line_no, col_no), referenced_by=None
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
