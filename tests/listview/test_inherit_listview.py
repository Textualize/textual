from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label


class MyListView(ListView):
    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        for n in range(20):
            yield ListView(Label(f"This is item {n}"))


class ListViewApp(App[None]):
    """ListView test app."""

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield MyListView()


async def test_inherited_list_view() -> None:
    """A self-populating inherited ListView should work as normal."""
    async with ListViewApp().run_test() as pilot:
        await pilot.press("tab")
        assert pilot.app.query_one(MyListView).index == 0
        await pilot.press("down")
        assert pilot.app.query_one(MyListView).index == 1
