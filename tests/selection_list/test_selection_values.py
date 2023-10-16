"""Unit tests dealing with the tracking of selection list values."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import SelectionList
from textual.widgets._selection_list import Selection


class SelectionListApp(App[None]):
    def __init__(self, default_state: bool = False, disabled: bool = False) -> None:
        super().__init__()
        self._default_state = default_state
        self._disabled = disabled

    def compose(self) -> ComposeResult:
        yield SelectionList[int](
            *[
                Selection(str(n), n, self._default_state, disabled=self._disabled)
                for n in range(50)
            ]
        )


async def test_empty_selected() -> None:
    """Selected should be empty when nothing is selected."""
    async with SelectionListApp().run_test() as pilot:
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_select_enabled() -> None:
    """Selected should contain a selected value."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select(0)
        assert pilot.app.query_one(SelectionList).selected == [0]


async def test_programatic_select_disabled() -> None:
    """Selected should contain a selected value."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select(0)
        assert pilot.app.query_one(SelectionList).selected == [0]


async def test_programatic_select_all_enabled() -> None:
    """Selected should contain all selected values."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select_all()
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_select_all_enabled_with_enabled_only() -> None:
    """Selected should contain all selected values."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select_all(True)
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_select_all_disabled() -> None:
    """Selected should contain all selected values."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select_all()
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_select_all_disabled_with_enabled_only() -> None:
    """Selected should contain no selected values."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.select_all(True)
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_deselect_enabled() -> None:
    """Selected should not contain a deselected value."""
    async with SelectionListApp(True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect(0)
        assert pilot.app.query_one(SelectionList).selected == list(range(50)[1:])


async def test_programatic_deselect_disabled() -> None:
    """Selected should not contain a deselected value."""
    async with SelectionListApp(True, True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect(0)
        assert pilot.app.query_one(SelectionList).selected == list(range(1, 50))


async def test_programatic_deselect_all_enabled() -> None:
    """Selected should not contain anything after deselecting all values."""
    async with SelectionListApp(True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect_all()
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_deselect_all_enabled_with_enabled_only() -> None:
    """Selected should not contain anything after deselecting all values."""
    async with SelectionListApp(True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect_all(True)
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_deselect_all_disabled() -> None:
    """Selected should not contain anything after deselecting all values."""
    async with SelectionListApp(True, True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect_all()
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_deselect_all_disabled_with_enabled_only() -> None:
    """Selected should not contain anything after deselecting all values."""
    async with SelectionListApp(True, True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.deselect_all(True)
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_toggle_enabled() -> None:
    """Selected should reflect a toggle."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        for n in range(25, 50):
            selection.select(n)
        for n in range(50):
            selection.toggle(n)
        assert pilot.app.query_one(SelectionList).selected == list(range(50)[:25])


async def test_programatic_toggle_disabled() -> None:
    """Selected should reflect a toggle."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        for n in range(25, 50):
            selection.select(n)
        for n in range(50):
            selection.toggle(n)
        assert pilot.app.query_one(SelectionList).selected == list(range(50)[:25])


async def test_programatic_toggle_all_enabled() -> None:
    """Selected should contain all values after toggling all on."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle_all()
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_toggle_all_enabled_with_enabled_only() -> None:
    """Selected should contain all values after toggling all on."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle_all(True)
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_toggle_all_disabled() -> None:
    """Selected should contain all values after toggling all on."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle_all()
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_programatic_toggle_all_disabled_with_enabled_only() -> None:
    """Selected should contain no values after toggling all on."""
    async with SelectionListApp(disabled=True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle_all(True)
        assert pilot.app.query_one(SelectionList).selected == []


async def test_programatic_toggle_all_disabled_and_selected_with_enabled_only() -> None:
    """Selected should contain all values after not toggling all on."""
    async with SelectionListApp(True, True).run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle_all(True)
        assert pilot.app.query_one(SelectionList).selected == list(range(50))


async def test_removal_of_selected_item() -> None:
    """Removing a selected selection should remove its value from the selected set."""
    async with SelectionListApp().run_test() as pilot:
        selection = pilot.app.query_one(SelectionList)
        selection.toggle(0)
        assert pilot.app.query_one(SelectionList).selected == [0]
        selection.remove_option_at_index(0)
        assert pilot.app.query_one(SelectionList).selected == []
