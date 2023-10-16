"""Unit tests aimed at testing the selection list messages.

Note that these tests only cover a subset of the public API of this widget.
The bulk of the API is inherited from OptionList, and as such there are
comprehensive tests for that. These tests simply cover the parts of the API
that have been modified by the child class.
"""

from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import OptionList, SelectionList
from textual.widgets._selection_list import Selection


class SelectionListApp(App[None]):
    """Test selection list application."""

    def __init__(self, disabled: bool = False) -> None:
        super().__init__()
        self.messages: list[tuple[str, int | None]] = []
        self._disabled = disabled

    def compose(self) -> ComposeResult:
        yield SelectionList[int](
            *[Selection(str(n), n, disabled=self._disabled) for n in range(10)]
        )

    @on(OptionList.OptionMessage)
    @on(SelectionList.SelectionMessage)
    @on(SelectionList.SelectedChanged)
    def _record(
        self,
        event: OptionList.OptionMessage
        | SelectionList.SelectionMessage
        | SelectionList.SelectedChanged,
    ) -> None:
        assert event.control == self.query_one(SelectionList)
        self.messages.append(
            (
                event.__class__.__name__,
                event.selection_index
                if isinstance(event, SelectionList.SelectionMessage)
                else None,
            )
        )


async def test_messages_on_startup() -> None:
    """There should be a highlighted message when a non-empty selection list first starts up."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_new_highlight() -> None:
    """Setting the highlight to a new option should result in a message."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).highlighted = 2
        await pilot.pause()
        assert pilot.app.messages[1:] == [("SelectionHighlighted", 2)]


async def test_toggle_when_enabled() -> None:
    """Toggling an enabled option should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle(0)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_toggle_when_disabled() -> None:
    """Toggling an disabled option should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle(0)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_toggle_when_enabled_via_user() -> None:
    """Toggling via the user when enabled should result in the correct messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.press("space")
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectionToggled", 0),
        ]


async def test_toggle_when_disabled_via_user() -> None:
    """Toggling via the user when disabled should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.press("space")
        await pilot.pause()
        assert pilot.app.messages == []


async def test_toggle_all_when_enabled() -> None:
    """Toggling all options when enabled should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_toggle_all_when_enabled_and_enabled_only() -> None:
    """Toggling all options when enabled and enabled_only should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_toggle_all_when_disabled() -> None:
    """Toggling all options disabled should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_toggle_all_when_disabled_and_enabled_only() -> None:
    """Toggling all options disabled should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle_all(True)
        await pilot.pause()
        assert pilot.app.messages == []


async def test_select_when_enabled() -> None:
    """Selecting all an enabled option should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(1)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_when_disabled() -> None:
    """Selecting all an option disabled should result a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(1)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_selected_when_enabled() -> None:
    """Selecting an option that is already selected should emit no extra message.."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(0)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(0)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_selected_when_disabled() -> None:
    """Selecting an option that is already selected should emit no extra message.."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(0)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(0)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_all_enabled() -> None:
    """Selecting all enabled options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_enabled_when_enabled_only() -> None:
    """Selecting all enabled options when enabled_only should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_disabled() -> None:
    """Selecting all disabled options should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_all_disabled_when_enabled_only() -> None:
    """Not selecting all disabled options should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == []


async def test_select_all_selected_and_enabled() -> None:
    """Selecting all when all are selected and enabled should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_enabled_when_enabled_only_in_the_first() -> None:
    """Selecting all when all are selected and enabled should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_enabled_when_enabled_only_in_the_second() -> None:
    """Selecting all when all are selected and enabled should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_enabled_when_enabled_only_on_both() -> None:
    """Selecting all when all are selected and enabled should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_disabled() -> None:
    """Selecting all when all are selected and disabled should result in no extra messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_disabled_when_enabled_only_in_the_first() -> None:
    """Selecting all when all are disabled should result in no extra messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_disabled_when_enabled_only_in_the_second() -> None:
    """Selecting all when all are disabled should result in no extra messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_all_selected_and_disabled_when_enabled_only_on_both() -> None:
    """Not selecting all when all are disabled should result in no extra messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == []


async def test_deselect_enabled() -> None:
    """Deselecting an enabled option should result in a message."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(1)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect(1)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_deselect_disabled() -> None:
    """Deselecting an disabled option should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(1)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect(1)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_deselect_deselected_and_enabled() -> None:
    """Deselecting a enabled deselected option should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect(0)
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_deselect_deselected_and_disabled() -> None:
    """Deselecting a disabled deselected option should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect(0)
        await pilot.pause()
        assert pilot.app.messages == []


async def test_deselect_all_enabled() -> None:
    """Deselecting all enabled deselected options should result in no additional messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_deselect_all_enabled_and_enabled_only() -> None:
    """Deselecting all enabled deselected options should result in no additional messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_deselect_all_disabled() -> None:
    """Deselecting all disabled deselected options should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == []


async def test_deselect_all_disabled_and_enabled_only() -> None:
    """Deselecting all disabled deselected options should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == []


async def test_select_then_deselect_all_enabled() -> None:
    """Selecting and then deselecting all enabled options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_enabled_when_enabled_only_in_the_first() -> None:
    """Selecting and then deselecting all enabled options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_enabled_when_enabled_only_in_the_second() -> None:
    """Selecting and then deselecting all enabled options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_enabled_when_enabled_only_on_both() -> None:
    """Selecting and then deselecting all enabled options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_disabled() -> None:
    """Selecting and then deselecting all disabled options should result in messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_disabled_when_enabled_only_in_the_first() -> None:
    """Selecting and then deselecting all disabled options should result in no messages."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == []
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == []


async def test_select_then_deselect_all_disabled_when_enabled_only_in_the_second() -> None:
    """Selecting and then deselecting all disabled options should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectedChanged", None),
        ]


async def test_select_then_deselect_all_disabled_when_enabled_only_on_both() -> None:
    """Selecting and then deselecting all disabled options should result in a message."""
    async with SelectionListApp(True).run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all(True)
        await pilot.pause()
        assert pilot.app.messages == []
        pilot.app.query_one(SelectionList).deselect_all(True)
        await pilot.pause()
        assert pilot.app.messages == []
