from __future__ import annotations

from textual.widget import Widget

from .. import events, on
from ..app import ComposeResult
from ..containers import Container, Horizontal
from ..message import Message
from ..reactive import reactive
from ..widget import Widget
from ..widgets import Label

__all__ = ["Collapsible"]


class Collapsible(Widget):
    """A collapsible container."""

    collapsed = reactive(True)

    DEFAULT_CSS = """
    Collapsible {
        width: 1fr;
        height: auto;
    }
    """

    class Title(Horizontal):
        DEFAULT_CSS = """
        Title {
            width: 100%;
            height: auto;
        }

        Title:hover {
            background: grey;
        }

        Title .label {
            padding: 0 0 0 1;
        }

        Title #collapsed-symbol {
            display:none;
        }

        Title.-collapsed #expanded-symbol {
            display:none;
        }

        Title.-collapsed #collapsed-symbol {
            display:block;
        }
        """

        def __init__(
            self,
            *,
            label: str,
            collapsed_symbol: str,
            expanded_symbol: str,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
        ) -> None:
            super().__init__(name=name, id=id, classes=classes, disabled=disabled)
            self.collapsed_symbol = collapsed_symbol
            self.expanded_symbol = expanded_symbol
            self.label = label

        class Toggle(Message):
            """Request toggle."""

        async def _on_click(self, event: events.Click) -> None:
            """Inform ancestor we want to toggle."""
            event.stop()
            self.post_message(self.Toggle())

        def compose(self) -> ComposeResult:
            """Compose right/down arrow and label."""
            yield Label(self.expanded_symbol, classes="label", id="expanded-symbol")
            yield Label(self.collapsed_symbol, classes="label", id="collapsed-symbol")
            yield Label(self.label, classes="label")

    class Contents(Container):
        DEFAULT_CSS = """
        Contents {
            width: 100%;
            height: auto;
            padding: 0 0 0 3;
        }

        Contents.-collapsed {
            display: none;
        }
        """

    def __init__(
        self,
        *children: Widget,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "►",
        expanded_symbol: str = "▼",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a Collapsible widget.

        Args:
            *children: Contents that will be collapsed/expanded.
            title: Title of the collapsed/expanded contents.
            collapsed: Default status of the contents.
            collapsed_symbol: Collapsed symbol before the title.
            expanded_symbol: Expanded symbol before the title.
            name: The name of the collapsible.
            id: The ID of the collapsible in the DOM.
            classes: The CSS classes of the collapsible.
            disabled: Whether the collapsible is disabled or not.
        """
        self._title = self.Title(
            label=title,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
        )
        self._contents_list: list[Widget] = list(children)
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.collapsed = collapsed

    def _on_title_toggle(self, event: Title.Toggle) -> None:
        event.stop()
        self.collapsed = not self.collapsed

    def watch_collapsed(self) -> None:
        for child in self._nodes:
            child.set_class(self.collapsed, "-collapsed")

    def compose(self) -> ComposeResult:
        yield from (
            child.set_class(self.collapsed, "-collapsed")
            for child in (
                self._title,
                self.Contents(*self._contents_list),
            )
        )

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the contents.

        Args:
            widget: A Widget to add.
        """
        self._contents_list.append(widget)
