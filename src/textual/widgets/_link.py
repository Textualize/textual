from __future__ import annotations

from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static


class Link(Static, can_focus=True):
    """A simple, clickable link that opens a URL."""

    DEFAULT_CSS = """
    Link {
        width: auto;
        height: auto;
        min-height: 1;
        color: $accent;
        text-style: underline;
        &:hover { color: $accent-lighten-1; }
        &:focus { text-style: bold reverse; }
    }
    """

    BINDINGS = [Binding("enter", "open_link", "Open link")]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter | Open the link in the browser. |    
    """

    text: reactive[str] = reactive("", layout=True)
    url: reactive[str] = reactive("")

    def __init__(
        self,
        text: str,
        *,
        url: str | None = None,
        tooltip: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """A link widget.

        Args:
            text: Text of the link.
            url: A URL to open, when clicked. If `None`, the `text` parameter will also be used as the url.
            tooltip: Optional tooltip.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.
        """
        super().__init__(
            text, name=name, id=id, classes=classes, disabled=disabled, markup=False
        )
        self.set_reactive(Link.text, text)
        self.set_reactive(Link.url, text if url is None else url)
        self.tooltip = tooltip

    def watch_text(self, text: str) -> None:
        self.update(text)

    def on_click(self) -> None:
        self.action_open_link()

    def action_open_link(self) -> None:
        if self.url:
            self.app.open_url(self.url)
