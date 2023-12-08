from __future__ import annotations

from rich.console import RenderableType
from rich.text import Text

from .. import events
from ..app import ComposeResult
from ..binding import Binding
from ..containers import Container
from ..css.query import NoMatches
from ..message import Message
from ..reactive import reactive
from ..widget import Widget

__all__ = ["Collapsible", "CollapsibleTitle"]


class CollapsibleTitle(Widget, can_focus=True):
    """Title and symbol for the Collapsible."""

    DEFAULT_CSS = """
    CollapsibleTitle {
        width: auto;
        height: auto;
        padding: 0 1 0 1;
    }

    CollapsibleTitle:hover {
        background: $foreground 10%;
        color: $text;
    }

    CollapsibleTitle:focus {
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [Binding("enter", "toggle", "Toggle collapsible", show=False)]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter | Toggle the collapsible. |
    """

    collapsed = reactive(True)

    def __init__(
        self,
        *,
        label: str,
        collapsed_symbol: str,
        expanded_symbol: str,
        collapsed: bool,
    ) -> None:
        super().__init__()
        self.collapsed_symbol = collapsed_symbol
        self.expanded_symbol = expanded_symbol
        self.label = label
        self.collapse = collapsed

    class Toggle(Message):
        """Request toggle."""

    async def _on_click(self, event: events.Click) -> None:
        """Inform ancestor we want to toggle."""
        event.stop()
        self.post_message(self.Toggle())

    def action_toggle(self) -> None:
        """Toggle the state of the parent collapsible."""
        self.post_message(self.Toggle())

    def render(self) -> RenderableType:
        """Compose right/down arrow and label."""
        if self.collapsed:
            return Text(f"{self.collapsed_symbol} {self.label}")
        else:
            return Text(f"{self.expanded_symbol} {self.label}")


class Collapsible(Widget):
    """A collapsible container."""

    collapsed = reactive(True)

    DEFAULT_CSS = """
    Collapsible {
        width: 1fr;
        height: auto;
        background: $boost;
        border-top: hkey $background;
        padding-bottom: 1;
        padding-left: 1;
    }

    Collapsible.-collapsed > Contents {
        display: none;
    }
    """

    class Toggled(Message):
        """Parent class subclassed by `Collapsible` messages.

        Can be handled with `on(Collapsible.Toggled)` if you want to handle expansions
        and collapsed in the same way, or you can handle the specific events individually.
        """

        def __init__(self, collapsible: Collapsible) -> None:
            """Create an instance of the message.

            Args:
                collapsible: The `Collapsible` widget that was toggled.
            """
            self.collapsible: Collapsible = collapsible
            """The collapsible that was toggled."""
            super().__init__()

        @property
        def control(self) -> Collapsible:
            """An alias for [Toggled.collapsible][textual.widgets.Collapsible.Toggled.collapsible]."""
            return self.collapsible

    class Expanded(Toggled):
        """Event sent when the `Collapsible` widget is expanded.

        Can be handled using `on_collapsible_expanded` in a subclass of
        [`Collapsible`][textual.widgets.Collapsible] or in a parent widget in the DOM.
        """

    class Collapsed(Toggled):
        """Event sent when the `Collapsible` widget is collapsed.

        Can be handled using `on_collapsible_collapsed` in a subclass of
        [`Collapsible`][textual.widgets.Collapsible] or in a parent widget in the DOM.
        """

    class Contents(Container):
        DEFAULT_CSS = """
        Contents {
            width: 100%;
            height: auto;
            padding: 1 0 0 3;
        }
        """

    def __init__(
        self,
        *children: Widget,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "▶",
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
        self._title = CollapsibleTitle(
            label=title,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
            collapsed=collapsed,
        )
        self._contents_list: list[Widget] = list(children)
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.collapsed = collapsed

    def _on_collapsible_title_toggle(self, event: CollapsibleTitle.Toggle) -> None:
        event.stop()
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.post_message(self.Collapsed(self))
        else:
            self.post_message(self.Expanded(self))

    def _watch_collapsed(self, collapsed: bool) -> None:
        """Update collapsed state when reactive is changed."""
        self._update_collapsed(collapsed)

    def _update_collapsed(self, collapsed: bool) -> None:
        """Update children to match collapsed state."""
        try:
            self._title.collapsed = collapsed
            self.set_class(collapsed, "-collapsed")
        except NoMatches:
            pass

    def _on_mount(self, event: events.Mount) -> None:
        """Initialise collapsed state."""
        self._update_collapsed(self.collapsed)

    def compose(self) -> ComposeResult:
        yield self._title
        yield self.Contents(*self._contents_list)

    def compose_add_child(self, widget: Widget) -> None:
        """When using the context manager compose syntax, we want to attach nodes to the contents.

        Args:
            widget: A Widget to add.
        """
        self._contents_list.append(widget)
