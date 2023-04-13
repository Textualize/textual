from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label, ListItem, ListView


class MyListView(ListView):
    """Test child class of a ListView."""

    BINDINGS = [Binding(key="s", action="set", description="Set")]

    def __init__(self, items: int = 0) -> None:
        super().__init__()
        self._items = items
        self.action_fired = False

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        for n in range(self._items):
            yield ListItem(Label(f"This is item {n}"))

    def action_set(self) -> None:
        self.action_fired = True


class ListViewApp(App[None]):
    """ListView test app."""

    def __init__(self, items: int = 0) -> None:
        super().__init__()
        self._items = items

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield MyListView(self._items)


async def test_empty_inherited_list_view() -> None:
    """An empty self-populating inherited ListView should work as expected."""
    async with ListViewApp().run_test() as pilot:
        await pilot.press("tab")
        assert pilot.app.query_one(MyListView).index is None
        await pilot.press("down")
        assert pilot.app.query_one(MyListView).index is None


async def test_populated_inherited_list_view() -> None:
    """A self-populating inherited ListView should work as normal."""
    async with ListViewApp(30).run_test() as pilot:
        await pilot.press("tab")
        assert pilot.app.query_one(MyListView).index == 0
        await pilot.press("down")
        assert pilot.app.query_one(MyListView).index == 1


async def test_actions_work_when_list_view_empty() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/2265"""
    async with ListViewApp().run_test() as pilot:
        await pilot.press("tab", "s")
        list_view = pilot.app.query_one(MyListView)
        assert list_view.action_fired
