from __future__ import annotations

from collections import deque
import io
from typing import (
    Callable,
    Deque,
    Generator,
    TypeVar,
    Generic,
    Union,
    Iterable,
)


class ParseError(Exception):
    """A parsing related exception."""
    pass


class ParseEOF(ParseError):
    """End of Stream."""


class Awaitable:
    """Holds the list of characters that will be processed by the parser."""
    __slots__: list[str] = []


class _Read(Awaitable):
    """Read the feed until a given number of characters is reached."""

    __slots__ = ["remaining"]

    def __init__(self, count: int) -> None:
        """
        Args:
            count (int): The count of characters to be read from the input.

        Returns:
            None
        """
        self.remaining = count

    def __repr__(self) -> str:
        return f"_Read({self.remaining})"


class _Read1(Awaitable):
    """Reads a single character from the input feed."""

    __slots__: list[str] = []


class _ReadUntil(Awaitable):
    """Reads the input feed until `max_bytes` is reached."""

    __slots__ = ["sep", "max_bytes"]

    def __init__(self, sep: str, max_bytes: int | None = None) -> None:
        """
        Args:
            sep (str): Sep defines the token that is used to delimit the input feed.
            max_bytes (int): The maxium number of bytes to read in the sequence.

        Returns:
            None
        """
        self.sep = sep
        self.max_bytes = max_bytes


class PeekBuffer(Awaitable):
    """Peek the current location in the buffer without advancing to the next index."""

    __slots__: list[str] = []


T = TypeVar("T")


TokenCallback = Callable[[T], None]


class Parser(Generic[T]):
    """Parses stdin to extract mouse codes and other input."""

    read = _Read
    read1 = _Read1
    read_until = _ReadUntil
    peek_buffer = PeekBuffer

    def __init__(self) -> None:
        self._buffer = io.StringIO()
        self._eof = False
        self._tokens: Deque[T] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Union[Awaitable, T] = next(self._gen)

    @property
    def is_eof(self) -> bool:
        """True if the end of the feed is reached."""

        return self._eof

    def reset(self) -> None:
        """Reset the input feed back to the starting position."""

        self._gen = self.parse(self._tokens.append)
        self._awaiting = next(self._gen)

    def feed(self, data: str) -> Iterable[T]:
        """Performs parsing on a feed of data.

        Args:
            data (str): The data that will be parsed.

        Returns:
            Iterable[T]: An Iterable of type T containing items returned by the parser.
        """
        if self._eof:
            raise ParseError("end of file reached") from None
        if not data:
            self._eof = True
            try:
                self._gen.send(self._buffer.getvalue())
            except StopIteration:
                raise ParseError("end of file reached") from None
            while self._tokens:
                yield self._tokens.popleft()

            self._buffer.truncate(0)
            return

        _buffer = self._buffer
        pos = 0
        tokens = self._tokens
        popleft = tokens.popleft
        data_size = len(data)

        while tokens:
            yield popleft()

        while pos < data_size or isinstance(self._awaiting, PeekBuffer):

            _awaiting = self._awaiting
            if isinstance(_awaiting, _Read1):
                self._awaiting = self._gen.send(data[pos : pos + 1])
                pos += 1

            elif isinstance(_awaiting, PeekBuffer):
                self._awaiting = self._gen.send(data[pos:])

            elif isinstance(_awaiting, _Read):
                remaining = _awaiting.remaining
                chunk = data[pos : pos + remaining]
                chunk_size = len(chunk)
                pos += chunk_size
                _buffer.write(chunk)
                remaining -= chunk_size
                if remaining:
                    _awaiting.remaining = remaining
                else:
                    _awaiting = self._gen.send(_buffer.getvalue())
                    _buffer.truncate(0)

            elif isinstance(_awaiting, _ReadUntil):
                chunk = data[pos:]
                _buffer.write(chunk)
                sep = _awaiting.sep
                sep_index = _buffer.getvalue().find(sep)

                if sep_index == -1:
                    pos += len(chunk)
                    if (
                        _awaiting.max_bytes is not None
                        and _buffer.tell() > _awaiting.max_bytes
                    ):
                        self._gen.throw(ParseError(f"expected {sep}"))
                else:
                    sep_index += len(sep)
                    if (
                        _awaiting.max_bytes is not None
                        and sep_index > _awaiting.max_bytes
                    ):
                        self._gen.throw(ParseError(f"expected {sep}"))
                    data = _buffer.getvalue()[sep_index:]
                    pos = 0
                    self._awaiting = self._gen.send(_buffer.getvalue()[:sep_index])
                    _buffer.truncate(0)

            while tokens:
                yield popleft()

    def parse(self, on_token: Callable[[T], None]) -> Generator[Awaitable, str, None]:
        """Parse data recieved from the input feed. This method should be overriden in
        the subclass.

        Args:
            on_token (Callable[[T], None]): A callable that defines the action for each token received.

        Returns:
            Generator[Awaitable, str, None]: A generator of awaitable, string or None.

        Example:

            The following example defines a subclass that will parse string inputs from the `feed` method.::

            class TestParser(Parser[str]):
                def parse(self, on_token: Callable[[str], None]) -> Generator[Awaitable, str, None]:
                    data = yield self.read1()
                    while True:
                        data = yield self.read1()
                        if not data:
                            break
                        on_token(data)
        """
        return


if __name__ == "__main__":
    data = "Where there is a Will there is a way!"

    class TestParser(Parser[str]):
        def parse(
            self, on_token: Callable[[str], None]
        ) -> Generator[Awaitable, str, None]:
            data = yield self.read1()
            while True:
                data = yield self.read1()
                if not data:
                    break
                on_token(data)

    test_parser = TestParser()

    for n in range(0, len(data), 5):
        for token in test_parser.feed(data[n : n + 5]):
            print(token)
    for token in test_parser.feed(""):
        print(token)
