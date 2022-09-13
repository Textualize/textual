from __future__ import annotations

from rich.console import RenderableType

from rich.text import Text
import rich.repr

from .. import events
from ..reactive import Reactive, watch
from ..widget import Widget


@rich.repr.auto
class Footer(Widget):

    DEFAULT_CSS = """
    Footer {
        background: $accent;
        color: $text;
        dock: bottom;
        height: 1;
    }
    Footer > .footer--highlight {    
        background: $accent-darken-1;         
    }

    Footer > .footer--highlight-key {        
        background: $secondary;                
        text-style: bold;         
    }

    Footer > .footer--key {
        text-style: bold;        
        background: $accent-darken-2;        
    }
    """

    COMPONENT_CLASSES = {
        "footer--description",
        "footer--key",
        "footer--highlight",
        "footer--highlight-key",
    }

    def __init__(self) -> None:
        super().__init__()
        self._key_text: Text | None = None

    highlight_key: Reactive[str | None] = Reactive(None)

    async def watch_highlight_key(self, value) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._key_text = None

    def on_mount(self) -> None:
        watch(self.app, "focused", self._focus_changed)

    def _focus_changed(self, focused: Widget | None) -> None:
        self.log("FOCUS CHANGED", focused)
        self._key_text = None
        self.refresh()

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlight_key = event.style.meta.get("key")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlight_key = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        base_style = self.rich_style
        text = Text(
            style=self.rich_style,
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        highlight_style = self.get_component_rich_style("footer--highlight")
        highlight_key_style = self.get_component_rich_style("footer--highlight-key")
        key_style = self.get_component_rich_style("footer--key")
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", highlight_key_style if hovered else key_style),
                (
                    f" {binding.description} ",
                    highlight_style if hovered else base_style,
                ),
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text

    def post_render(self, renderable):
        return renderable

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        return self._key_text
