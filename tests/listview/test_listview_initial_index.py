import pytest

from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView


@pytest.mark.parametrize(
    "initial_index,expected_index",
    [
        (0, 1),
        (1, 1),
        (2, 4),
        (3, 4),
        (4, 4),
        (5, 5),
        (6, 7),
        (7, 7),
        (8, 1),
    ],
)
async def test_listview_initial_index(initial_index, expected_index) -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4449"""

    class ListViewDisabledItemsApp(App[None]):
        def compose(self) -> ComposeResult:
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
                initial_index=initial_index,
            )

    app = ListViewDisabledItemsApp()
    async with app.run_test() as pilot:
        list_view = pilot.app.query_one(ListView)
        assert list_view._index == expected_index
