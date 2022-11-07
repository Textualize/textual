from textual.reactive import reactive
from textual.widget import Widget


class ListItem(Widget):
    DEFAULT_CSS = "ListItem {height: auto;}"

    highlighted = reactive(False)

    def watch_highlighted(self, value: bool) -> None:
        self.set_class(value, "--highlight")
