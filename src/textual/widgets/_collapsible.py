from __future__ import annotations

from textual.widget import Widget

from .. import events, on
from ..app import ComposeResult
from ..containers import Container, Horizontal
from ..message import Message
from ..reactive import reactive
from ..widget import Widget
from ._label import Label

__all__ = ["Collapsible"]


class Collapsible(Widget):
    """A collapsible container."""

    collapsed = reactive(True)

    DEFAULT_CSS = """
    Collapsible {
        width: 100%;
        height: auto;
    }
    """

    class Summary(Horizontal):
        DEFAULT_CSS = """
        Summary {
            width: 100%;
            height: auto;
        }

        Summary:hover {
            background: grey;
        }

        Summary .label {
            padding: 0 0 0 1;
        }

        Summary #collapsed-label {
            display:none;
        }

        Summary.-collapsed #expanded-label {
            display:none;
        }

        Summary.-collapsed #collapsed-label {
            display:block;
        }
        """

        def __init__(
            self,
            *,
            collapsed_label: str = "►",
            expanded_label: str = "▼",
            label: str = "Toggle",
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
        ) -> None:
            super().__init__(name=name, id=id, classes=classes, disabled=disabled)
            self.label = label
            self.collapsed_label = collapsed_label
            self.expanded_label = expanded_label

        class Toggle(Message):
            """Request toggle."""

        async def _on_click(self, event: events.Click) -> None:
            """Inform ancestor we want to toggle."""
            self.post_message(self.Toggle())

        def compose(self) -> ComposeResult:
            """Compose right/down arrow and label."""
            yield Label(self.expanded_label, classes="label", id="expanded-label")
            yield Label(self.collapsed_label, classes="label", id="collapsed-label")
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
        summary: str = "Toggle",
        collapsed: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a Collapsible widget.

        Args:
            *children: Contents that will be collapsed/expanded.
            summary: Summary of the collapsed/expanded contents.
            collapsed: Default status of the contents.
            name: The name of the collapsible.
            id: The ID of the collapsible in the DOM.
            classes: The CSS classes of the collapsible.
            disabled: Whether the collapsible is disabled or not.
        """
        self.summary: str = summary
        self._contents_list: list[Widget] = list(children)
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.collapsed = collapsed

    @on(Summary.Toggle)
    def _update_collapsed(self) -> None:
        self.collapsed = not self.collapsed

    def watch_collapsed(self) -> None:
        for child in self._nodes:
            child.set_class(self.collapsed, "-collapsed")

    def compose(self) -> ComposeResult:
        yield from (
            child.set_class(self.collapsed, "-collapsed")
            for child in (
                self.Summary(label=self.summary),
                self.Contents(*self._contents_list),
            )
        )

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the contents.

        Args:
            widget: A Widget to add.
        """
        self._contents_list.append(widget)
