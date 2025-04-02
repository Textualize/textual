from __future__ import annotations

from collections import deque
from typing import Callable, Deque, Generator, Generic, Iterable, NamedTuple, TypeVar

from textual._time import get_time


class ParseError(Exception):
    """Base class for parse related errors."""


class ParseEOF(ParseError):
    """End of Stream."""


class ParseTimeout(ParseError):
    """Read has timed out."""


class Read1(NamedTuple):
    """Reads a single character."""

    timeout: float | None = None
    """Optional timeout in seconds."""


class Peek1(NamedTuple):
    """Reads a single character, but does not advance the parser position."""

    timeout: float | None = None
    """Optional timeout in seconds."""


T = TypeVar("T")
TokenCallback = Callable[[T], None]


class Parser(Generic[T]):
    """Base class for a simple parser."""

    read1 = Read1
    peek1 = Peek1

    def __init__(self) -> None:
        self._eof = False
        self._tokens: Deque[T] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Read1 | Peek1 = next(self._gen)
        self._timeout_time: float | None = None

    @property
    def is_eof(self) -> bool:
        """Is the parser at the end of the file (i.e. exhausted)?"""
        return self._eof

    def tick(self) -> Iterable[T]:
        """Call at regular intervals to check for timeouts."""
        if self._timeout_time is not None and get_time() >= self._timeout_time:
            self._timeout_time = None
            self._awaiting = self._gen.throw(ParseTimeout())
            while self._tokens:
                yield self._tokens.popleft()

    def feed(self, data: str) -> Iterable[T]:
        """Feed data to be parsed.

        Args:
            data: Data to parser.

        Raises:
            ParseError: If the data could not be parsed.

        Yields:
            T: A generic data type.
        """
        if self._eof:
            raise ParseError("end of file reached") from None

        tokens = self._tokens
        popleft = tokens.popleft

        if not data:
            self._eof = True
            try:
                self._gen.throw(ParseEOF())
            except StopIteration:
                pass
            while tokens:
                yield popleft()
            return

        pos = 0
        data_size = len(data)

        while tokens:
            yield popleft()

        while pos < data_size:
            _awaiting = self._awaiting
            if isinstance(_awaiting, Read1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos])
                pos += 1
            elif isinstance(_awaiting, Peek1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos])

            if self._awaiting.timeout is not None:
                self._timeout_time = get_time() + self._awaiting.timeout

            while tokens:
                yield popleft()

    def parse(
        self, token_callback: TokenCallback
    ) -> Generator[Read1 | Peek1, str, None]:
        """Implement to parse a stream of text.

        Args:
            token_callback: Callable to report a successful parsed data type.

        Yields:
            ParseAwaitable: One of `self.read1` or `self.peek1`
        """
        yield from ()
