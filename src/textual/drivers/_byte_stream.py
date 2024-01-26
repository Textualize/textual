from __future__ import annotations

import io
from collections import deque
from typing import (
    Callable,
    Deque,
    Generator,
    Generic,
    Iterable,
    NamedTuple,
    Tuple,
    TypeVar,
)

from typing_extensions import TypeAlias


class ParseError(Exception):
    """Parse related errors."""


class ParseEOF(ParseError):
    """End of Stream."""


class Awaitable:
    """Base class for an parser awaitable."""

    __slots__: list[str] = []


class _Read(Awaitable):
    """Read a predefined number of bytes."""

    __slots__ = ["remaining"]

    def __init__(self, count: int) -> None:
        self.remaining = count


class _Read1(Awaitable):
    """Read a single byte."""

    __slots__: list[str] = []


TokenType = TypeVar("TokenType")

ByteStreamTokenCallback: TypeAlias = Callable[[TokenType], None]


class ByteStreamParser(Generic[TokenType]):
    """A parser to feed in binary data and generate a sequence of tokens."""

    read = _Read
    read1 = _Read1

    def __init__(self) -> None:
        """Initialize the parser."""
        self._buffer = io.BytesIO()
        self._eof = False
        self._tokens: Deque[TokenType] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Awaitable | TokenType = next(self._gen)

    @property
    def is_eof(self) -> bool:
        """Is the parser at the end of file?"""
        return self._eof

    def feed(self, data: bytes) -> Iterable[TokenType]:
        """Feed the parser some data, return an iterable of tokens."""
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

        while pos < data_size:
            _awaiting = self._awaiting
            if isinstance(_awaiting, _Read1):
                self._awaiting = self._gen.send(data[pos : pos + 1])
                pos += 1
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
                    self._awaiting = self._gen.send(_buffer.getvalue())
                    _buffer.seek(0)
                    _buffer.truncate()

            while tokens:
                yield popleft()

    def parse(
        self, on_token: ByteStreamTokenCallback
    ) -> Generator[Awaitable, bytes, None]:
        """Implement in a sub-class to define parse behavior.

        Args:
            on_token: A callable which accepts the token type, and returns None.

        """
        yield from ()


class BytePacket(NamedTuple):
    """A type and payload."""

    type: str
    payload: bytes


class ByteStream(ByteStreamParser[Tuple[str, bytes]]):
    """A stream of packets in the following format.

    1 Byte for the type.
    4 Bytes for the big endian encoded size
    Arbitrary payload

    """

    def parse(
        self, on_token: ByteStreamTokenCallback
    ) -> Generator[Awaitable, bytes, None]:
        read1 = self.read1
        read = self.read
        from_bytes = int.from_bytes
        while not self.is_eof:
            packet_type = (yield read1()).decode("utf-8", "ignore")
            size = from_bytes((yield read(4)), "big")
            payload = (yield read(size)) if size else b""
            on_token(BytePacket(packet_type, payload))
