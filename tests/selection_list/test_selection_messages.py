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


class SelectionListApp(App[None]):
    """Test selection list application."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[tuple[str, int | None]] = []

    def compose(self) -> ComposeResult:
        yield SelectionList[int](*[(str(n), n) for n in range(10)])

    @on(OptionList.OptionMessage)
    @on(SelectionList.SelectionMessage)
    @on(SelectionList.SelectedChanged)
    def _record(
        self,
        event: (
            OptionList.OptionMessage
            | SelectionList.SelectionMessage
            | SelectionList.SelectedChanged
        ),
    ) -> None:
        assert event.control == self.query_one(SelectionList)
        self.messages.append(
            (
                event.__class__.__name__,
                (
                    event.selection_index
                    if isinstance(event, SelectionList.SelectionMessage)
                    else None
                ),
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


async def test_toggle() -> None:
    """Toggling an option should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle(0)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectionToggled", 0),
        ]


async def test_toggle_via_user() -> None:
    """Toggling via the user should result in the correct messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.press("space")
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
            ("SelectionToggled", 0),
        ]


async def test_toggle_all() -> None:
    """Toggling all options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).toggle_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select() -> None:
    """Selecting all an option should result in a message."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select(1)
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_selected() -> None:
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


async def test_select_all() -> None:
    """Selecting all options should result in messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).select_all()
        await pilot.pause()
        assert pilot.app.messages == [
            ("SelectionHighlighted", 0),
            ("SelectedChanged", None),
        ]


async def test_select_all_selected() -> None:
    """Selecting all when all are selected should result in no extra messages."""
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


async def test_deselect() -> None:
    """Deselecting an option should result in a message."""
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


async def test_deselect_deselected() -> None:
    """Deselecting a deselected option should result in no extra messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect(0)
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_deselect_all() -> None:
    """Deselecting all deselected options should result in no additional messages."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.pause()
        pilot.app.query_one(SelectionList).deselect_all()
        await pilot.pause()
        assert pilot.app.messages == [("SelectionHighlighted", 0)]


async def test_select_then_deselect_all() -> None:
    """Selecting and then deselecting all options should result in messages."""
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
