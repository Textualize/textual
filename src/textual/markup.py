from __future__ import annotations

import rich.repr
from rich.text import Text


@rich.repr.auto
class Markup:
    def __init__(self, content: str | Text = "", *, no_style: bool = False) -> None:
        """Marked up Test.

        This is essentially a immutable wrapper around Rich Text.

        Args:
            content: Either a string or a Text instance.
            no_style: Disable mar
        """
        if isinstance(content, str):
            _content = Text(content) if no_style else Text.from_markup(content)
        else:
            _content = content.copy()
        self._content = _content

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._content.markup

    def __rich__(self) -> Text:
        return self._content
