from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea()
        text_area.load_text(TEXT)
        yield text_area


async def test_insert_text_start():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello")
        assert text_area.text == "Hello" + TEXT
        assert text_area.cursor_location == (0, 5)


async def test_insert_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.cursor_location = (2, 5)
        text_area.insert_text("Hello,\nworld!")
        assert text_area.cursor_location == (3, 6)
        assert (
            text_area.text
            == """I must not fear.
Fear is the mind-killer.
Fear Hello,
world!is the little-death that brings total obliteration.
I will face my fear.
"""
        )


async def test_delete_left():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.cursor_location = (0, 6)
        await pilot.press("backspace")
        assert text_area.text == "Hello world!"


async def test_delete_left_start():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        await pilot.press("backspace")
        assert text_area.text == "Hello, world!"


async def test_delete_left_end():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.cursor_location = (0, 13)
        await pilot.press("backspace")
        assert text_area.text == "Hello, world"


async def test_delete_right():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.cursor_location = (0, 13)
        await pilot.press("delete")
        assert text_area.text == "Hello, world!"
