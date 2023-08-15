"""Tests editing the document using the API (insert_range etc.)

The tests in this module directly call the edit APIs on the TextArea rather
than going via bindings.

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


async def test_insert_text_start():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello")
        assert text_area.text == "Hello" + TEXT
        assert text_area.cursor_location == (0, 0)


async def test_insert_text_start_move_cursor():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello", move_cursor=True)
        assert text_area.text == "Hello" + TEXT
        assert text_area.cursor_location == (0, 5)


async def test_insert_newlines_start():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("\n\n\n")
        assert text_area.text == "\n\n\n" + TEXT


async def test_insert_newlines_end():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("\n\n\n", location=(4, 0))
        assert text_area.text == TEXT + "\n\n\n"


async def test_insert_windows_newlines():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        # Although we're inserting windows newlines, the configured newline on
        # the Document inside the TextArea will be "\n", so when we check TextArea.text
        # we expect to see "\n".
        text_area.insert_text("\r\n\r\n\r\n")
        assert text_area.text == "\n\n\n" + TEXT


async def test_insert_old_mac_newlines():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("\r\r\r")
        assert text_area.text == "\n\n\n" + TEXT


async def test_insert_text_non_cursor_location():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello", location=(4, 0))
        assert text_area.text == TEXT + "Hello"
        assert text_area.selection == Selection.cursor((0, 0))


async def test_insert_text_non_cursor_location_move_cursor():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello", location=(4, 0), move_cursor=True)
        assert text_area.text == TEXT + "Hello"
        assert text_area.selection == Selection.cursor((4, 5))


async def test_insert_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((2, 5))
        text_area.insert_text("Hello,\nworld!")
        expected_content = """\
I must not fear.
Fear is the mind-killer.
Fear Hello,
world!is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.cursor_location == (2, 5)  # Cursor didn't move
        assert text_area.text == expected_content


async def test_insert_multiline_text_move_cursor():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((2, 5))
        text_area.insert_text("Hello,\nworld!", move_cursor=True)
        expected_content = """\
I must not fear.
Fear is the mind-killer.
Fear Hello,
world!is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.cursor_location == (3, 6)  # Cursor moved to end of insert
        assert text_area.text == expected_content


async def test_insert_range_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        # replace "Fear is the mind-killer\nFear is the little death...\n"
        # with "Hello,\nworld!\n"
        text_area.insert_text_range(
            "Hello,\nworld!\n", from_location=(1, 0), to_location=(3, 0)
        )
        expected_content = """\
I must not fear.
Hello,
world!
I will face my fear.
"""
        assert text_area.selection == Selection.cursor((0, 0))  # cursor didnt move
        assert text_area.text == expected_content


async def test_insert_range_multiline_text_move_cursor():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        # replace "Fear is the mind-killer\nFear is the little death..."
        text_area.insert_text_range(
            "Hello,\nworld!\n",
            from_location=(1, 0),
            to_location=(3, 0),
            move_cursor=True,
        )
        expected_content = """\
I must not fear.
Hello,
world!
I will face my fear.
"""
        assert text_area.selection == Selection.cursor(
            (3, 0)
        )  # cursor moves to end of insert
        assert text_area.text == expected_content


async def test_delete_range_within_line():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        deleted_text = text_area.delete_range((0, 6), (0, 10))
        assert deleted_text == " not"
        expected_text = """\
I must fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.selection == Selection.cursor((0, 0))  # cursor didnt move
        assert text_area.text == expected_text


async def test_delete_range_within_line_move_cursor():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        deleted_text = text_area.delete_range((0, 6), (0, 10), move_cursor=True)
        assert deleted_text == " not"
        expected_text = """\
I must fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.selection == Selection.cursor((0, 6))  # cursor moved
        assert text_area.text == expected_text


async def test_delete_range_multiple_lines():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        deleted_text = text_area.delete_range((1, 0), (3, 0))
        assert text_area.selection == Selection.cursor((0, 0))
        assert (
            text_area.text
            == """\
I must not fear.
I will face my fear.
"""
        )
        assert (
            deleted_text
            == """\
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
"""
        )


async def test_delete_range_empty_document():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("")
        deleted_text = text_area.delete_range((0, 0), (1, 0))
        assert deleted_text == ""
        assert text_area.text == ""


async def test_clear():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.clear()


async def test_clear_empty_document():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("")
        text_area.clear()
