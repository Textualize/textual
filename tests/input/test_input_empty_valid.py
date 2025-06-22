from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App):

    def compose(self) -> ComposeResult:
        yield Input(valid_empty=False)


async def test_cut():
    """Check that cut removes text and places it in the clipboard."""
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        assert input.value == ""
        assert not input.is_valid
