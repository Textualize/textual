from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, ClassVar, Optional

import rich.repr
from rich.text import Text

from .. import events

if TYPE_CHECKING:
    from ..app import RenderResult
    from ..screen import Screen

from ..binding import Binding
from ..reactive import reactive
from ..widget import Widget


@rich.repr.auto
class Footer(Widget):
    """A simple footer widget which docks itself to the bottom of the parent container."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "footer--description",
        "footer--key",
        "footer--highlight",
        "footer--highlight-key",
    }
    """
    | Class | Description |
    | :- | :- |
    | `footer--description` | Targets the descriptions of the key bindings. |
    | `footer--highlight` | Targets the highlighted key binding. |
    | `footer--highlight-key` | Targets the key portion of the highlighted key binding. |
    | `footer--key` | Targets the key portions of the key bindings. |
    """

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

    highlight_key: reactive[str | None] = reactive[Optional[str]](None)

    def __init__(self) -> None:
        super().__init__()
        self._key_text: Text | None = None
        self.auto_links = False

    async def watch_highlight_key(self) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._key_text = None
        self.refresh()

    def _on_mount(self, _: events.Mount) -> None:
        self.screen.bindings_updated_signal.subscribe(self, self._bindings_changed)

    def _bindings_changed(self, _screen: Screen) -> None:
        self._key_text = None
        self.refresh()

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlight_key = event.style.meta.get("key")

    def _on_leave(self, _: events.Leave) -> None:
        """Clear any highlight when the mouse leaves the widget"""
        self.highlight_key = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()

    def _make_key_text(self) -> Text:
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
        description_style = self.get_component_rich_style("footer--description")

        bindings = [
            (binding, enabled)
            for (_, binding, enabled) in self.screen.active_bindings.values()
            if binding.show
        ]

        action_to_bindings: defaultdict[str, list[tuple[Binding, bool]]] = defaultdict(
            list
        )
        for binding, enabled in bindings:
            action_to_bindings[binding.action].append((binding, enabled))

        app_focus = self.app.app_focus
        for _, _bindings in action_to_bindings.items():
            binding, enabled = _bindings[0]
            if binding.key_display is None:
                key_display = self.app.get_key_display(binding.key)
                if key_display is None:
                    key_display = binding.key.upper()
            else:
                key_display = binding.key_display
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", highlight_key_style if hovered else key_style),
                (
                    f" {binding.description} ",
                    highlight_style if hovered else base_style + description_style,
                ),
                meta=(
                    {
                        "@click": f"app.check_bindings('{binding.key}')",
                        "key": binding.key,
                    }
                    if enabled and app_focus
                    else {}
                ),
            )
            if not enabled or not app_focus:
                key_text.stylize("dim")
            text.append_text(key_text)
        return text

    def notify_style_update(self) -> None:
        self._key_text = None

    def post_render(self, renderable):
        return renderable

    def render(self) -> RenderResult:
        if self._key_text is None:
            self._key_text = self._make_key_text()
        return self._key_text
