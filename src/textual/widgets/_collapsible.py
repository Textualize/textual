from __future__ import annotations

from textual.widget import Widget
from ..widget import Widget
from ..message import Message
from .. import events, on
from ._label import Label
from ..containers import Horizontal
from ..app import ComposeResult

__all__ = ["Collapsible"]

class CollapseToggle(Horizontal):
    DEFAULT_CSS = """
    CollapseToggle {
        width: 100%;
        height: auto;
    }

    CollapseToggle .label {
        padding: 0 0 0 1;
    }

    CollapseToggle .collapsed-label {
        display:none;
    }

    CollapseToggle.-collapsed .expanded-label {
        display:none;
    }

    CollapseToggle.-collapsed .collapsed-label {
        display:block;
    }

    """
    def __init__(self,
                 *,
                 collapsed_icon: str = "►",
                 expanded_icon: str = "▼",
                 label: str = "Toggle",
                 collapsed: bool = True,
                 name: str | None = None,
                 id: str | None = None,
                 classes: str | None = None,
                 disabled: bool = False) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.label = label
        self.collapsed_icon = collapsed_icon
        self.expanded_icon = expanded_icon
        self.collapsed = collapsed
        self.set_class(self.collapsed, '-collapsed')

    class Toggle(Message):
        """Request toggle."""

    async def _on_click(self, event: events.Click) -> None:
        """Inform ancestor we want to toggle."""
        self.collapsed = not self.collapsed
        self.set_class(self.collapsed, '-collapsed')
        self.post_message(self.Toggle())

    def compose(self) -> ComposeResult:
        """Compose right/down arrow and label."""
        yield Label(self.expanded_icon, classes="label expanded-label")
        yield Label(self.collapsed_icon, classes="label collapsed-label")
        yield Label(self.label, classes='label')


class Collapsible(Widget):
    """A collapsible container."""
    # TODO: Adjust gap between contents.
    # TODO: Wrap contents within one container.
    # TODO: Expose `collapsed` as a reactivity handle if needed.

    def __init__(
        self,
        *,
        summary: str = "Toggle",
        collapsed: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a Collapsible widget.

        Args:
            summary: Summary of the collapsed/expanded contents.
            collapsed: Default status of the contents.
            name: The name of the collapsible.
            id: The ID of the collapsible in the DOM.
            classes: The CSS classes of the collapsible.
            disabled: Whether the collapsible is disabled or not.
        """
        self._summary = CollapseToggle(label=summary, collapsed=collapsed)
        self._contents: list[Widget] = []
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    @on(CollapseToggle.Toggle)
    def _adjust_contents_visibility(self) -> None:
        for content in self._contents:
            content.display = not self._summary.collapsed

    def compose(self) -> ComposeResult:
        yield self._summary
        yield from self._contents

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the switcher.

        Args:
            widget: A Widget to add.
        """
        widget.display = not self._summary.collapsed
        self._contents.append(widget)
