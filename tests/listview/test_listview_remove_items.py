from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView


class EmptyListViewApp(App[None]):
    def compose(self) -> ComposeResult:
        yield ListView()


async def test_listview_pop_empty_raises_index_error():
    app = EmptyListViewApp()
    async with app.run_test() as pilot:
        listview = pilot.app.query_one(ListView)
        with pytest.raises(IndexError) as excinfo:
            listview.pop()
        assert "pop from empty list" in str(excinfo.value)


class ListViewApp(App[None]):
    def __init__(self, initial_index: int | None = None):
        super().__init__()
        self.initial_index = initial_index
        self.highlighted = []

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
            initial_index=self.initial_index,
        )

    def _on_list_view_highlighted(self, message: ListView.Highlighted) -> None:
        if message.item is None:
            self.highlighted.append(None)
        else:
            self.highlighted.append(str(message.item.children[0].renderable))


async def test_listview_remove_items() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4735"""
    app = ListViewApp()
    async with app.run_test() as pilot:
        listview = pilot.app.query_one(ListView)
        assert len(listview) == 9
        await listview.remove_items(range(4, 9))
        assert len(listview) == 4


@pytest.mark.parametrize(
    "initial_index, pop_index, expected_new_index, expected_highlighted",
    [
        (2, 2, 2, ["2", "3"]),  # Remove highlighted item
        (0, 0, 0, ["0", "1"]),  # Remove first item when highlighted
        (8, None, 7, ["8", "7"]),  # Remove last item when highlighted
        (4, 2, 3, ["4", "4"]),  # Remove item before the highlighted index
        (4, -2, 4, ["4"]),  # Remove item after the highlighted index
    ],
)
async def test_listview_pop_updates_index_and_highlighting(
    initial_index, pop_index, expected_new_index, expected_highlighted
) -> None:
    """Regression test for https://github.com/Textualize/textual/issues/5114"""
    app = ListViewApp(initial_index)
    async with app.run_test() as pilot:
        listview = pilot.app.query_one(ListView)

        await listview.pop(pop_index)
        await pilot.pause()

        assert listview.index == expected_new_index
        assert listview._nodes[expected_new_index].highlighted is True
        assert app.highlighted == expected_highlighted


@pytest.mark.parametrize(
    "initial_index, remove_indices, expected_new_index, expected_highlighted",
    [
        (2, [2], 2, ["2", "3"]),  # Remove highlighted item
        (0, [0], 0, ["0", "1"]),  # Remove first item when highlighted
        (8, [-1], 7, ["8", "7"]),  # Remove last item when highlighted
        (4, [2, 1], 2, ["4", "4"]),  # Remove items before the highlighted index
        (4, [-2, 5], 4, ["4"]),  # Remove items after the highlighted index
        (4, range(0, 9), None, ["4", None]),  # Remove all items
    ],
)
async def test_listview_remove_items_updates_index_and_highlighting(
    initial_index, remove_indices, expected_new_index, expected_highlighted
) -> None:
    """Regression test for https://github.com/Textualize/textual/issues/5114"""
    app = ListViewApp(initial_index)
    async with app.run_test() as pilot:
        listview = pilot.app.query_one(ListView)

        await listview.remove_items(remove_indices)
        await pilot.pause()

        assert listview.index == expected_new_index
        if expected_new_index is not None:
            assert listview._nodes[expected_new_index].highlighted is True
        assert app.highlighted == expected_highlighted


if __name__ == "__main__":
    app = ListViewApp()
    app.run()
