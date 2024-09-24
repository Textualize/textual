from __future__ import annotations

from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from typing import TYPE_CHECKING

from rich import box
from rich.table import Table
from rich.text import Text

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.screen import Screen


class BindingsTable(Static):
    """A widget to display bindings."""

    COMPONENT_CLASSES = {
        "bindings-table--key",
        "bindings-table--description",
        "bindings-table--divider",
        "bindings-table--header",
    }

    DEFAULT_CSS = """
    BindingsTable {
        width: auto;
        height: auto;
    }
    """

    def render_bindings_table(self) -> Table:
        """Render a table with all the key bindings.

        Returns:
            A Rich Table.
        """

        bindings = self.screen.active_bindings.values()

        key_style = self.get_component_rich_style("bindings-table--key")
        divider_transparent = (
            self.get_component_styles("bindings-table--divider").color.a == 0
        )
        table = Table(
            padding=(0, 0),
            show_header=False,
            box=box.SIMPLE if divider_transparent else box.HORIZONTALS,
            border_style=self.get_component_rich_style("bindings-table--divider"),
        )
        table.add_column("", justify="right")

        header_style = self.get_component_rich_style("bindings-table--header")
        previous_namespace: object = None
        for namespace, _bindings in groupby(bindings, key=itemgetter(0)):
            table_bindings = list(_bindings)
            if not table_bindings:
                continue

            if namespace.BINDING_GROUP_TITLE:
                title = Text(namespace.BINDING_GROUP_TITLE, end="")
                title.stylize(header_style)
                table.add_row("", title)

            action_to_bindings: defaultdict[str, list[tuple[Binding, bool, str]]]
            action_to_bindings = defaultdict(list)
            for _, binding, enabled, tooltip in table_bindings:
                action_to_bindings[binding.action].append((binding, enabled, tooltip))

            description_style = self.get_component_rich_style(
                "bindings-table--description"
            )

            def render_description(binding: Binding) -> Text:
                """Render description text from a binding."""
                text = Text.from_markup(
                    binding.description, end="", style=description_style
                )
                if binding.tooltip:
                    text.append(" ")
                    text.append(binding.tooltip, "dim")
                return text

            get_key_display = self.app.get_key_display
            for multi_bindings in action_to_bindings.values():
                binding, enabled, tooltip = multi_bindings[0]
                key_display = " ".join(
                    get_key_display(binding) for binding, _, _ in multi_bindings
                )
                table.add_row(
                    Text(key_display, style=key_style),
                    render_description(binding),
                )
            if namespace != previous_namespace:
                table.add_section()

            previous_namespace = namespace

        return table

    def render(self) -> Table:
        return self.render_bindings_table()


class KeyPanel(VerticalScroll, can_focus=False):
    """
    Shows bindings for currently focused widget.
    """

    DEFAULT_CSS = """
    KeyPanel {                    
        split: right;
        width: 33%;
        min-width: 30;              
        max-width: 60;    
        border-left: vkey $foreground 30%;
        padding: 0 1;
        height: 1fr;
        padding-right: 1;
        align: center top;

        &> BindingsTable > .bindings-table--key {
            color: $secondary;           
            text-style: bold;
            padding: 0 1;
        }

        &> BindingsTable > .bindings-table--description {
            color: $foreground;
        }

        &> BindingsTable > .bindings-table--divider {
            color: transparent;
        }

        &> BindingsTable > .bindings-table--header {
            text-style: dim italic;
        }

        #bindings-table {
            width: auto;
            height: auto;
        }      
    }
    """

    DEFAULT_CLASSES = "-textual-system"

    def compose(self) -> ComposeResult:
        yield BindingsTable(shrink=True, expand=False)

    async def on_mount(self) -> None:
        async def bindings_changed(screen: Screen) -> None:
            if not screen.app.app_focus:
                return
            if self.is_attached and screen is self.screen:
                self.refresh(recompose=True)

        self.set_class(self.app.ansi_color, "-ansi-scrollbar")
        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)
