from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget


class ListItem(Widget, can_focus=False):
    DEFAULT_CSS = """
    ListItem {
        color: $text;
        height: auto;
        background: $panel-lighten-1;
        overflow: hidden hidden;
    }
    ListItem > Widget :hover {
        background: $boost;
    }
    ListItem.--highlight {
        background: $accent;
    }
    ListItem > Widget {
        height: auto;
    }
    """
    highlighted = reactive(False)

    def on_click(self, event: events.Click) -> None:
        self.emit_no_wait(self.ChildSelected(self))

    def watch_highlighted(self, value: bool) -> None:
        self.set_class(value, "--highlight")

    class ChildSelected(Message):
        pass
