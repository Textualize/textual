from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea()


async def test_cut():
    """Check that cut removes text and places it in the clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+x")
        assert text_area.text == "Hello, Wod"
        assert app.clipboard == "rl"


async def test_copy():
    """Check that copy places text in the clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+c")
        assert text_area.text == "Hello, World"
        assert app.clipboard == "rl"


async def test_paste():
    """Check that paste copies text from the local clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press(
            "shift+left", "shift+left", "shift+left", "shift+left", "shift+left"
        )
        await pilot.press("ctrl+c")
        assert text_area.text == "Hello, World"
        assert app.clipboard == "World"
        await pilot.press("ctrl+v")
        assert text_area.text == "Hello, World"
        await pilot.press("ctrl+v")
        assert text_area.text == "Hello, WorldWorld"
