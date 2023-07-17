"""See https://github.com/Textualize/textual/pull/2930 for the introduction of these tests."""

from textual import on
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import SelectionList

class SelectionListApp(App[None]):
    """Test selection list application."""

    def __init__(self) -> None:
        super().__init__()
        self.clicks: list[int] = []

    def compose(self) -> ComposeResult:
        yield SelectionList[int](*[(str(n), n) for n in range(10)])

    @on(SelectionList.SelectionToggled)
    def _record(self, event: SelectionList.SelectionToggled) -> None:
        assert event.control == self.query_one(SelectionList)
        self.clicks.append(event.selection_index)


async def test_click_on_prompt() -> None:
    """It should be possible to toggle a selection by clicking on the prompt."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.click(SelectionList, Offset(5,1))
        await pilot.pause()
        assert pilot.app.clicks == [0]


async def test_click_on_checkbox() -> None:
    """It should be possible to toggle a selection by clicking on the checkbox."""
    async with SelectionListApp().run_test() as pilot:
        assert isinstance(pilot.app, SelectionListApp)
        await pilot.click(SelectionList, Offset(3,1))
        await pilot.pause()
        assert pilot.app.clicks == [0]

if __name__ == "__main__":
    SelectionListApp().run()
