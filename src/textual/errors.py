from __future__ import annotations


class TextualError(Exception):
    pass


class NoWidget(TextualError):
    pass
