from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView


class ListViewDisabledItemsApp(App[None]):
    def compose(self) -> ComposeResult:
        self.highlighted = []
        yield ListView(
            ListItem(Label("0"), disabled=True),
            ListItem(Label("1")),
            ListItem(Label("2"), disabled=True),
            ListItem(Label("3"), disabled=True),
            ListItem(Label("4")),
            ListItem(Label("5")),
            ListItem(Label("6"), disabled=True),
            ListItem(Label("7")),
            ListItem(Label("8"), disabled=True),
        )

    def _on_list_view_highlighted(self, message: ListView.Highlighted) -> None:
        if message.item is None:
            self.highlighted.append(None)
        else:
            self.highlighted.append(str(message.item.children[0].renderable))


async def test_keyboard_navigation_with_disabled_items() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3881."""

    app = ListViewDisabledItemsApp()
    async with app.run_test() as pilot:
        for _ in range(5):
            await pilot.press("down")
        for _ in range(5):
            await pilot.press("up")

    assert app.highlighted == [
        "1",
        "4",
        "5",
        "7",
        "5",
        "4",
        "1",
    ]
