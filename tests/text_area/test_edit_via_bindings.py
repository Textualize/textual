"""Tests some edits using the keyboard.

All tests in this module should press keys on the keyboard which edit the document,
and check that the document content is updated as expected, as well as the cursor
location.

Note that more extensive testing for editing is done at the Document level.
"""

from textual.app import App, ComposeResult
from textual.document import Selection
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


async def test_single_keypress_printable_character():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.press("x")
        assert text_area.text == "x" + TEXT


async def test_single_keypress_enter():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.press("enter")
        assert text_area.text == "\n" + TEXT


async def test_delete_left():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.move_cursor((0, 6))
        await pilot.press("backspace")
        assert text_area.text == "Hello world!"
        assert text_area.selection == Selection.cursor((0, 5))


async def test_delete_left_start():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        await pilot.press("backspace")
        assert text_area.text == "Hello, world!"
        assert text_area.selection == Selection.cursor((0, 0))


async def test_delete_left_end():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.move_cursor((0, 13))
        await pilot.press("backspace")
        assert text_area.text == "Hello, world"
        assert text_area.selection == Selection.cursor((0, 12))


async def test_delete_right():
    """Pressing 'delete' deletes the character to the right of the cursor."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("Hello, world!")
        text_area.move_cursor((0, 13))
        await pilot.press("delete")
        assert text_area.text == "Hello, world!"
        assert text_area.selection == Selection.cursor((0, 13))


async def test_delete_right_end_of_line():
    """Pressing 'delete' at the end of the line merges this line with the line below."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("hello\nworld!")
        end_of_line = text_area.get_cursor_line_end_location()
        text_area.move_cursor(end_of_line)
        await pilot.press("delete")
        assert text_area.selection == Selection.cursor((0, 5))
        assert text_area.text == "helloworld!"
