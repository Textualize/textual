from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from rich.table import Table
from rich.text import Text

from ..app import ComposeResult
from ..binding import Binding
from ..containers import VerticalScroll
from ..reactive import reactive
from ..widgets import Static

if TYPE_CHECKING:
    from ..screen import Screen


class KeyPanel(VerticalScroll):
    COMPONENT_CLASSES = {"footer-key--key", "footer-key--description"}

    DEFAULT_CSS = """
    KeyPanel {        
    
        
        split: right;
        # layer: textual-system-high;
        width: 33%;
        min-width: 30;
        # overlay: screen;
       
        max-width: 60;    
        border-left: vkey $foreground 30%;
        
        padding: 1 1;
        height: 1fr;

        padding-right: 1;

        &>.footer-key--key {
            color: $secondary;
           
            text-style: bold;
            padding: 0 1;
        }

        &>.footer-key--description {
            color: $text;
        }

        #bindings-table {
            width: auto;
            height: auto;
        }
      
    }
    """

    upper_case_keys = reactive(False)
    """Upper case key display."""
    ctrl_to_caret = reactive(True)
    """Convert 'ctrl+' prefix to '^'."""
    _bindings_ready = reactive(False, repaint=False, recompose=True)

    def render_bindings_table(self) -> Table:
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
            """Render description text from a binding."""
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
                    binding.key_display
                    or self.app.get_key_display(
                        binding.key,
                        upper_case_keys=self.upper_case_keys,
                        ctrl_to_caret=self.ctrl_to_caret,
                    ),
                    style=key_style,
                ),
                render_description(binding),
            )

        return table

    def compose(self) -> ComposeResult:
        table = self.render_bindings_table()
        self.log(table)
        yield Static(table, id="bindings-table", shrink=True, expand=False)

    async def on_mount(self) -> None:
        self.shrink = False

        async def bindings_changed(screen: Screen) -> None:
            self._bindings_ready = True
            if self.is_attached and screen is self.screen:
                await self.recompose()

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)
        await self.recompose()

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)
