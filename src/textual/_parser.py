from collections import deque
from typing import (
    Callable,
    Deque,
    Generator,
    TypeVar,
    Generic,
    Union,
    Iterator,
    Iterable,
)


class ParseError(Exception):
    pass


class ParseEOF(ParseError):
    """End of Stream."""


class Awaitable:
    __slots__: list[str] = []

    def validate(self, chunk: bytes) -> None:
        """Raise any ParseErrors"""


class _ReadBytes(Awaitable):
    __slots__ = ["remaining"]

    def __init__(self, count: int) -> None:
        self.remaining = count

    def __repr__(self) -> str:
        return f"_ReadBytes({self.remaining})"


T = TypeVar("T")


class Parser(Generic[T]):
    read = _ReadBytes

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._eof = False
        self._tokens: Deque[T] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Union[Awaitable, T] = next(self._gen)

    @property
    def is_eof(self) -> bool:
        return self._eof

    def reset(self) -> None:
        self._gen = self.parse(self._tokens.append)
        self._awaiting = next(self._gen)

    def feed(self, data: bytes) -> Iterable[T]:
        if self._eof:
            raise ParseError("end of file reached")
        if not data:
            self._eof = True
            try:
                self._gen.send(self._buffer[:])
            except StopIteration:
                raise ParseError("end of file reached") from None
            while self._tokens:
                yield self._tokens.popleft()

            del self._buffer[:]
            return
            # self._gen.throw(ParseError("unexpected eof of file"))

        _buffer = self._buffer
        pos = 0
        while pos < len(data):

            if isinstance(self._awaiting, _ReadBytes):

                remaining = self._awaiting.remaining
                chunk = data[pos : pos + remaining]
                chunk_size = len(chunk)
                pos += chunk_size
                try:
                    self._awaiting.validate(chunk)
                except ParseError as error:
                    self._awaiting = self._gen.throw(error)
                    continue
                _buffer.extend(chunk)
                remaining -= chunk_size
                if remaining:
                    self._awaiting.remaining = remaining
                else:
                    self._awaiting = self._gen.send(_buffer[:])
                    del _buffer[:]

            while self._tokens:
                yield self._tokens.popleft()

    def parse(self, on_token: Callable[[T], None]) -> Generator[Awaitable, bytes, None]:
        return
        yield


if __name__ == "__main__":
    data = b"Where there is a Will there is a way!"

    class TestParser(Parser[bytes]):
        def parse(
            self, on_token: Callable[[bytes], None]
        ) -> Generator[Awaitable, bytes, None]:
            while data := (yield self.read(3)):
                print("-", data)
                on_token(data)

    test_parser = TestParser()

    import time

    for n in range(0, len(data), 2):
        for token in test_parser.feed(data[n : n + 2]):
            print(bytes(token))
    for token in test_parser.feed(b""):
        print(bytes(token))
