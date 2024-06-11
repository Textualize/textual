from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import rich.repr
from rich.text import Text

from ..app import ComposeResult
from ..binding import Binding
from ..containers import ScrollableContainer
from ..reactive import reactive
from ..widget import Widget

if TYPE_CHECKING:
    from ..screen import Screen


@rich.repr.auto
class FooterKey(Widget):
    COMPONENT_CLASSES = {
        "footer-key--key",
        "footer-key--description",
    }

    DEFAULT_CSS = """
    FooterKey {
        width: auto;
        height: 1;
        background: $panel;
        color: $text-muted;
        .footer-key--key {
            color: $secondary;
            background: $panel;
            text-style: bold;
        }

        &:light .footer-key--key {
            color: $primary;
        }

        &:hover {
            background: $panel-darken-2;
            color: $text;
            .footer-key--key {
                background: $panel-darken-2;
            }
        }

        &.-disabled {
            text-style: dim;
            background: $panel;
            &:hover {
                .footer-key--key {
                    background: $panel;
                }
            }
        }

    }
    """

    upper_case_keys = reactive(False)
    ctrl_to_caret = reactive(True)
    compact = reactive(True)

    def __init__(
        self,
        key: str,
        key_display: str,
        description: str,
        action: str,
        disabled: bool = False,
    ) -> None:
        self.key = key
        self.key_display = key_display
        self.description = description
        self.action = action
        self._disabled = disabled
        super().__init__(classes="-disabled" if disabled else "")

    def render(self) -> Text:
        key_style = self.get_component_rich_style("footer-key--key")
        description_style = self.get_component_rich_style("footer-key--description")
        key_display = self.key_display
        if self.upper_case_keys:
            key_display = key_display.upper()
        if self.ctrl_to_caret and key_display.lower().startswith("ctrl+"):
            key_display = "^" + key_display.split("+", 1)[1]
        description = self.description
        if self.compact:
            label_text = Text.assemble(
                (key_display, key_style), " ", (description, description_style)
            )
        else:
            label_text = Text.assemble(
                (f" {key_display} ", key_style), (description, description_style), " "
            )
        label_text.stylize_before(self.rich_style)
        return label_text

    async def on_mouse_down(self) -> None:
        if self._disabled:
            self.app.bell()
        else:
            await self.app.check_bindings(self.key)

    def _watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")


@rich.repr.auto
class Footer(ScrollableContainer, can_focus=False, can_focus_children=False):
    DEFAULT_CSS = """
    Footer {
        layout: grid;
        grid-columns: auto;
        background: $panel;
        color: $text;
        dock: bottom;
        height: 1;
        scrollbar-size: 0 0;
        &.-compact {
            grid-gutter: 1;
        }
    }
    """

    upper_case_keys = reactive(False)
    """Upper case key display."""
    ctrl_to_caret = reactive(True)
    """Convert 'ctrl+' prefix to '^'."""
    compact = reactive(False)
    """Display in compact style."""
    _bindings_ready = reactive(False, repaint=False)
    """True if the bindings are ready to be displayed."""

    def compose(self) -> ComposeResult:
        if not self._bindings_ready:
            return
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

        self.styles.grid_size_columns = len(action_to_bindings)
        for multi_bindings in action_to_bindings.values():
            binding, enabled = multi_bindings[0]
            yield FooterKey(
                binding.key,
                binding.key_display or self.app.get_key_display(binding.key),
                binding.description,
                binding.action,
                disabled=not enabled,
            ).data_bind(
                Footer.upper_case_keys,
                Footer.ctrl_to_caret,
                Footer.compact,
            )

    def on_mount(self) -> None:
        async def bindings_changed(screen: Screen) -> None:
            self._bindings_ready = True
            if self.is_attached and screen is self.screen:
                await self.recompose()

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")
