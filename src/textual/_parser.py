from __future__ import annotations

import io
from collections import deque
from typing import Callable, Deque, Generator, Generic, Iterable, NamedTuple, TypeVar

from ._time import get_time


class ParseError(Exception):
    pass


class ParseEOF(ParseError):
    """End of Stream."""


class ParseTimeout(ParseError):
    """Read has timed out."""


class Read1(NamedTuple):
    timeout: float | None = None


class Peek1(NamedTuple):
    timeout: float | None = None


T = TypeVar("T")


TokenCallback = Callable[[T], None]


class Parser(Generic[T]):
    read1 = Read1
    peek1 = Peek1

    def __init__(self) -> None:
        self._buffer = io.StringIO()
        self._eof = False
        self._tokens: Deque[T] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Read1 | Peek1 = next(self._gen)
        self._timeout_time: float | None = None

    @property
    def is_eof(self) -> bool:
        return self._eof

    def reset(self) -> None:
        self._gen = self.parse(self._tokens.append)
        self._awaiting = next(self._gen)
        self._timeout_time = None

    def tick(self) -> Iterable[T]:
        """Call at regular intervals to check for timeouts."""
        if self._timeout_time is not None and get_time() >= self._timeout_time:
            self._timeout_time = None
            self._awaiting = self._gen.throw(ParseTimeout())
            while self._tokens:
                yield self._tokens.popleft()

    def feed(self, data: str) -> Iterable[T]:
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

        pos = 0
        tokens = self._tokens
        popleft = tokens.popleft
        data_size = len(data)

        while tokens:
            yield popleft()

        while pos < data_size:
            _awaiting = self._awaiting
            if isinstance(_awaiting, Read1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos : pos + 1])
                pos += 1
            elif isinstance(_awaiting, Peek1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos : pos + 1])

            if self._awaiting.timeout is not None:
                self._timeout_time = get_time() + self._awaiting.timeout

            while tokens:
                yield popleft()

    def parse(
        self, on_token: Callable[[T], None]
    ) -> Generator[Read1 | Peek1, str, None]:
        yield from ()


if __name__ == "__main__":
    data = "Where there is a Will there is a way!"

    class TestParser(Parser[str]):
        def parse(
            self, on_token: Callable[[str], None]
        ) -> Generator[Read1 | Peek1, str, None]:
            while True:
                try:
                    data = yield self.read1(0.1)
                except ParseTimeout:
                    print("TIMEOUT")
                    continue
                if not data:
                    break
                on_token(data)

    test_parser = TestParser()
    from time import sleep

    for n in range(0, len(data), 5):
        test_parser.tick()
        for token in test_parser.feed(data[n : n + 5]):
            print(token)
        sleep(0.1)
    for token in test_parser.feed(""):
        print(token)
