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


class BindingsTable(Static):
    COMPONENT_CLASSES = {"bindings-table--key", "bindings-table--description"}

    DEFAULT_CSS = """
    BindingsTable {
        width: auto;
        height: auto;
    }
    """

    upper_case_keys = reactive(False)
    """Upper case key display."""
    ctrl_to_caret = reactive(True)
    """Convert 'ctrl+' prefix to '^'."""

    def render_bindings_table(self) -> Table:
        """Render a table with all the key bindings.

        Returns:
            A Rich Table.
        """
        bindings = [
            (binding, enabled, tooltip)
            for (_, binding, enabled, tooltip) in self.screen.active_bindings.values()
        ]
        action_to_bindings: defaultdict[str, list[tuple[Binding, bool, str]]]
        action_to_bindings = defaultdict(list)
        for binding, enabled, tooltip in bindings:
            action_to_bindings[binding.action].append((binding, enabled, tooltip))

        table = Table.grid(padding=(0, 1))
        key_style = self.get_component_rich_style("bindings-table--key")
        description_style = self.get_component_rich_style("bindings-table--description")

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

    def render(self) -> Table:
        return self.render_bindings_table()


class KeyPanel(VerticalScroll, can_focus=False):
    DEFAULT_CSS = """
    KeyPanel {                    
        split: right;
        width: 33%;
        min-width: 30;              
        max-width: 60;    
        border-left: vkey $foreground 30%;        
        padding: 1 1;
        height: 1fr;
        padding-right: 1;

        &> BindingsTable > .bindings-table--key {
            color: $secondary;           
            text-style: bold;
            padding: 0 1;
        }

        &> BindingsTable > .bindings-table--description {
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

    def compose(self) -> ComposeResult:
        yield BindingsTable(shrink=True, expand=False).data_bind(
            KeyPanel.upper_case_keys,
            KeyPanel.ctrl_to_caret,
        )

    async def on_mount(self) -> None:
        async def bindings_changed(screen: Screen) -> None:
            if self.is_attached and screen is self.screen:
                self.refresh()

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)
