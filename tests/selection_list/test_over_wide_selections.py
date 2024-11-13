"""See https://github.com/Textualize/textual/issues/2900 for the reason behind these tests."""

from textual.app import App, ComposeResult
from textual.widgets import SelectionList


class SelectionListApp(App[None]):
    """Test selection list application."""

    CSS = """
    OptionList {
        width: 20;
    }
    """

    def compose(self) -> ComposeResult:
        yield SelectionList[int](*[(f"{n} ", n) for n in range(10)])


async def test_over_wide_options() -> None:
    """Options wider than the widget should not be an issue."""
    async with SelectionListApp().run_test() as pilot:
        assert pilot.app.query_one(SelectionList).highlighted == 0
        await pilot.pause()
        assert pilot.app.query_one(SelectionList).highlighted == 0


if __name__ == "__main__":
    SelectionListApp().run()
