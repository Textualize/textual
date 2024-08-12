from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from rich.table import Table
from rich.text import Text

from ..binding import Binding
from ..reactive import reactive
from ..widgets import Static

if TYPE_CHECKING:
    from ..screen import Screen


class KeyPanel(Static):
    COMPONENT_CLASSES = {
        "footer-key--key",
        "footer-key--description",
    }

    DEFAULT_CSS = """
    KeyPanel {        
        layout: vertical;
        dock: right;
        # layer: textual-high;
        width: 20;
        # min-width: 20;
        max-width: 33%;    
        # border-left: vkey $foreground 30%;
        
        padding: 0 1;
        height: 1fr;

        border-left: vkey $primary;
        

        padding-right: 1;

        &>.footer-key--key {
            color: $secondary;
           
            text-style: bold;
            padding: 0 1;
        }

        &>.footer-key--description {
            color: $text;
        }

      

      
    }
    """

    _bindings_ready = reactive(False, repaint=False, recompose=True)

    def update_bindings(self) -> None:
        bindings = [
            (binding, enabled, tooltip)
            for (_, binding, enabled, tooltip) in self.screen.active_bindings.values()
        ]
        action_to_bindings: defaultdict[str, list[tuple[Binding, bool, str]]]
        action_to_bindings = defaultdict(list)
        for binding, enabled, tooltip in bindings:
            action_to_bindings[binding.action].append((binding, enabled, tooltip))

        table = Table.grid(padding=(0, 1))

        key_style = self.get_component_rich_style("footer-key--key")
        description_style = self.get_component_rich_style("footer-key--description")

        def render_description(binding: Binding) -> Text:
            text = Text.from_markup(
                binding.description, end="", style=description_style
            )
            if binding.tooltip:
                text.append(" ")
                text.append(binding.tooltip, "dim")
            return text

        table.add_column("", justify="right")
        for multi_bindings in action_to_bindings.values():
            binding, enabled, tooltip = multi_bindings[0]
            table.add_row(
                Text(
                    binding.key_display or self.app.get_key_display(binding.key),
                    style=key_style,
                ),
                render_description(binding),
            )

        self.update(table)

    def on_mount(self) -> None:
        async def bindings_changed(screen: Screen) -> None:
            self._bindings_ready = True
            if self.is_attached and screen is self.screen:
                self.update_bindings()

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)
