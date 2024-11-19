from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, ListItem, ListView


class ListViewIndexApp(App):
    CSS = """
    ListView {
        height: 10;
    }
    """

    data = reactive(list(range(6)))

    def __init__(self) -> None:
        super().__init__()
        self._menu = ListView()

    def compose(self) -> ComposeResult:
        yield self._menu

    async def watch_data(self, data: "list[int]") -> None:
        await self._menu.remove_children()
        await self._menu.extend((ListItem(Label(str(value))) for value in data))

        new_index = len(self._menu) - 1
        self._menu.index = new_index

    async def on_ready(self):
        self.data = list(range(0, 30, 2))


if __name__ == "__main__":
    app = ListViewIndexApp()
    app.run()
