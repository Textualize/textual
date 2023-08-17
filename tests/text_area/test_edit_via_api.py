"""Tests editing the document using the API (insert_range etc.)

The tests in this module directly call the edit APIs on the TextArea rather
than going via bindings.

Note that more extensive testing for editing is done at the Document level.
"""

from textual.app import App, ComposeResult
from textual.document import EditResult, Selection
from textual.widgets import TextArea

TEXT = """\
I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea()
        text_area.load_text(TEXT)
        yield text_area


async def test_insert_text_start_maintain_selection_offset():
    """Ensure that we can maintain the offset between the location
    an insert happens and the location of the selection."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((0, 5))
        text_area.insert_text("Hello", location=(0, 0))
        assert text_area.text == "Hello" + TEXT
        assert text_area.selection == Selection.cursor((0, 10))


async def test_insert_text_start():
    """If we don't maintain the selection offset, the cursor jumps
    to the end of the edit and the selection is empty."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((0, 5))
        text_area.insert_text("Hello", location=(0, 0), maintain_selection_offset=False)
        assert text_area.text == "Hello" + TEXT
        assert text_area.selection == Selection.cursor((0, 5))


async def test_insert_newlines_start():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("\n\n\n")
        assert text_area.text == "\n\n\n" + TEXT
        assert text_area.selection == Selection.cursor((3, 0))


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


async def test_insert_text_non_cursor_location_dont_maintain_offset():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert_text("Hello", location=(4, 0), maintain_selection_offset=False)
        assert text_area.text == TEXT + "Hello"
        assert text_area.selection == Selection.cursor((4, 5))


async def test_insert_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((2, 5))
        text_area.insert_text("Hello,\nworld!", maintain_selection_offset=False)
        expected_content = """\
I must not fear.
Fear is the mind-killer.
Fear Hello,
world!is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.cursor_location == (3, 6)  # Cursor moved to end of insert
        assert text_area.text == expected_content


async def test_insert_multiline_text_maintain_offset():
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
        # The insert happens at the cursor (default location)
        # Offset is maintained - we inserted 1 line so cursor shifts
        # down 1 line, and along by the length of the last insert line.
        assert text_area.cursor_location == (3, 6)
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


async def test_insert_range_multiline_text_maintain_selection():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # To begin with, the user selects the word "face"
        text_area.selection = Selection((3, 7), (3, 11))
        assert text_area.selected_text == "face"

        # Text is inserted via the API in a way that shifts
        # the start and end locations of the word "face" in
        # both the horizontal and vertical directions.
        text_area.insert_text_range(
            "Hello,\nworld!\n123\n456",
            from_location=(1, 0),
            to_location=(3, 0),
        )
        expected_content = """\
I must not fear.
Hello,
world!
123
456I will face my fear.
"""
        # Despite this insert, the selection locations are updated
        # and the word face is still highlighted. This ensures that
        # if text is insert programmatically, a user that is typing
        # won't lose their place - the cursor will maintain the same
        # relative position in the document as before.
        assert text_area.selected_text == "face"
        assert text_area.selection == Selection((4, 10), (4, 14))
        assert text_area.text == expected_content


async def test_delete_range_within_line():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((0, 11), (0, 15))
        assert text_area.selected_text == "fear"

        # Delete some text before the selection location.
        result = text_area.delete_range((0, 6), (0, 10))

        # Even though the word has 'shifted' left, it's still selected.
        assert text_area.selection == Selection((0, 7), (0, 11))
        assert text_area.selected_text == "fear"

        # We've recorded exactly what text was replaced in the EditResult
        assert result == EditResult(
            end_location=(0, 6),
            replaced_text=" not",
        )

        expected_text = """\
I must fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.text == expected_text


async def test_delete_range_within_line_dont_maintain_offset():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.delete_range((0, 6), (0, 10), maintain_selection_offset=False)
    expected_text = """\
I must fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""
    assert text_area.selection == Selection.cursor((0, 6))  # cursor moved
    assert text_area.text == expected_text


async def test_delete_range_multiple_lines_selection_above():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # User has selected text on the first line...
        text_area.selection = Selection((0, 2), (0, 6))
        assert text_area.selected_text == "must"

        # Some lines below are deleted...
        result = text_area.delete_range((1, 0), (3, 0))

        # The selection is not affected at all.
        assert text_area.selection == Selection((0, 2), (0, 6))

        # We've recorded the text that was deleted in the ReplaceResult.
        # Lines of index 1 and 2 were deleted. Since the end
        # location of the selection is (3, 0), the newline
        # marker is included in the deletion.
        expected_replaced_text = """\
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
"""
        assert result == EditResult(
            end_location=(1, 0),
            replaced_text=expected_replaced_text,
        )
        assert (
            text_area.text
            == """\
I must not fear.
I will face my fear.
"""
        )


async def test_delete_range_empty_document():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("")
        result = text_area.delete_range((0, 0), (1, 0))
        assert result.replaced_text == ""
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
