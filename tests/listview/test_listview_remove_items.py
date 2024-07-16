from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label


class ListViewApp(App[None]):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("0")),
            ListItem(Label("1")),
            ListItem(Label("2")),
            ListItem(Label("3")),
            ListItem(Label("4")),
            ListItem(Label("5")),
            ListItem(Label("6")),
            ListItem(Label("7")),
            ListItem(Label("8")),
        )


async def test_listview_remove_items() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4735"""
    app = ListViewApp()
    async with app.run_test() as pilot:
        listview = pilot.app.query_one(ListView)
        assert len(listview) == 9
        await listview.remove_items(range(4, 9))
        assert len(listview) == 4


if __name__ == "__main__":
    app = ListViewApp()
    app.run()
