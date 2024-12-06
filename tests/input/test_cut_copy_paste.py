from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App):
    def compose(self) -> ComposeResult:
        yield Input()


async def test_cut():
    """Check that cut removes text and places it in the clipboard."""
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        await pilot.click(input)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+x")
        assert input.value == "Hello, Wod"
        assert app.clipboard == "rl"


async def test_copy():
    """Check that copy places text in the clipboard."""
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        await pilot.click(input)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+c")
        assert input.value == "Hello, World"
        assert app.clipboard == "rl"


async def test_paste():
    """Check that paste copies text from the local clipboard."""
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        await pilot.click(input)
        await pilot.press(*"Hello, World")
        await pilot.press(
            "shift+left", "shift+left", "shift+left", "shift+left", "shift+left"
        )
        await pilot.press("ctrl+c")
        assert input.value == "Hello, World"
        assert app.clipboard == "World"
        await pilot.press("ctrl+v")
        assert input.value == "Hello, World"
        await pilot.press("ctrl+v")
        assert input.value == "Hello, WorldWorld"
