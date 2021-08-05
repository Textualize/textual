from __future__ import annotations

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
import rich.repr

from .. import events
from ..reactive import Reactive
from ..widget import Widget


@rich.repr.auto
class Footer(Widget):
    def __init__(self) -> None:
        self.keys: list[tuple[str, str]] = []
        super().__init__()
        self.layout_size = 1
        self._key_text: Text | None = None

    highlight_key: Reactive[str | None] = Reactive(None)

    async def watch_highlight_key(self, value) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._key_text = None

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlight_key = event.style.meta.get("key")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlight_key = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield "keys", self.keys

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style="white on dark_green",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", "reverse" if hovered else "default on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        return self._key_text
