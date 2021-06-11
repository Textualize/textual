from typing import Iterable, Generator

from .keys import Keys
from ._parser import Awaitable, Parser, TokenCallback
from ._ansi_sequences import ANSI_SEQUENCES


class XTermParser(Parser[Keys]):
    def parse(self, on_token: TokenCallback) -> Generator[Awaitable, Keys, None]:

        ESC = "\x1b"
        read1 = self.read1
        get_ansi_sequence = ANSI_SEQUENCES.get
        while not self.is_eof:
            character: str = yield read1()
            if character == ESC:
                sequence = character
                while True:
                    sequence += yield read1()
                    keys = get_ansi_sequence(sequence, None)
                    if keys is not None:
                        on_token(keys)
                        break
            else:
                on_token(character)


if __name__ == "__main__":
    parser = XTermParser()

    import os
    import sys

    for token in parser.feed(sys.stdin.read(20)):
        print(token)
