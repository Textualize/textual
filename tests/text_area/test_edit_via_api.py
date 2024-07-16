"""Tests editing the document using the API (replace etc.)

The tests in this module directly call the edit APIs on the TextArea rather
than going via bindings.

Note that more extensive testing for editing is done at the Document level.
"""

import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import EditResult, Selection

TEXT = """\
I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""

SIMPLE_TEXT = """\
ABCDE
FGHIJ
KLMNO
PQRST
UVWXY
Z
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
        text_area.insert("Hello", location=(0, 0))
        assert text_area.text == "Hello" + TEXT
        assert text_area.selection == Selection.cursor((0, 10))


async def test_insert_text_start():
    """The document is correctly updated on inserting at the start.
    If we don't maintain the selection offset, the cursor jumps
    to the end of the edit and the selection is empty."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((0, 5))
        text_area.insert("Hello", location=(0, 0), maintain_selection_offset=False)
        assert text_area.text == "Hello" + TEXT
        assert text_area.selection == Selection.cursor((0, 5))


async def test_insert_empty_string():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")

        text_area.insert("", location=(0, 3))

        assert text_area.text == "0123456789"


async def test_replace_empty_string():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")

        text_area.replace("", start=(0, 3), end=(0, 7))

        assert text_area.text == "012789"


@pytest.mark.parametrize(
    "cursor_location,insert_location,cursor_destination",
    [
        ((0, 3), (0, 2), (0, 4)),  # API insert just before cursor
        ((0, 3), (0, 3), (0, 4)),  # API insert at cursor location
        ((0, 3), (0, 4), (0, 3)),  # API insert just after cursor
        ((0, 3), (0, 5), (0, 3)),  # API insert just after cursor
    ],
)
async def test_insert_character_near_cursor_maintain_selection_offset(
    cursor_location,
    insert_location,
    cursor_destination,
):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("012345")
        text_area.move_cursor(cursor_location)
        text_area.insert("X", location=insert_location)
        assert text_area.selection == Selection.cursor(cursor_destination)


@pytest.mark.parametrize(
    "cursor_location,insert_location,cursor_destination",
    [
        ((1, 0), (0, 0), (2, 0)),  # API insert before cursor row
        ((0, 0), (0, 0), (1, 0)),  # API insert right at cursor row
        ((0, 0), (1, 0), (0, 0)),  # API insert after cursor row
    ],
)
async def test_insert_newline_around_cursor_maintain_selection_offset(
    cursor_location,
    insert_location,
    cursor_destination
):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor(cursor_location)
        text_area.insert("X\n", location=insert_location)
        assert text_area.selection == Selection.cursor(cursor_destination)


async def test_insert_newlines_start():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert("\n\n\n")
        assert text_area.text == "\n\n\n" + TEXT
        assert text_area.selection == Selection.cursor((3, 0))


async def test_insert_newlines_end():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert("\n\n\n", location=(4, 0))
        assert text_area.text == TEXT + "\n\n\n"


async def test_insert_windows_newlines():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        # Although we're inserting windows newlines, the configured newline on
        # the Document inside the TextArea will be "\n", so when we check TextArea.text
        # we expect to see "\n".
        text_area.insert("\r\n\r\n\r\n")
        assert text_area.text == "\n\n\n" + TEXT


async def test_insert_old_mac_newlines():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert("\r\r\r")
        assert text_area.text == "\n\n\n" + TEXT


async def test_insert_text_non_cursor_location():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.insert("Hello", location=(4, 0))
        assert text_area.text == TEXT + "Hello"
        assert text_area.selection == Selection.cursor((0, 0))


async def test_insert_text_non_cursor_location_dont_maintain_offset():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((2, 3), (3, 5))

        result = text_area.insert(
            "Hello",
            location=(4, 0),
            maintain_selection_offset=False,
        )

        assert result == EditResult(
            end_location=(4, 5),
            replaced_text="",
        )
        assert text_area.text == TEXT + "Hello"

        # Since maintain_selection_offset is False, the selection
        # is reset to a cursor and goes to the end of the insert.
        assert text_area.selection == Selection.cursor((4, 5))


async def test_insert_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor((2, 5))
        text_area.insert("Hello,\nworld!", maintain_selection_offset=False)
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
        result = text_area.insert("Hello,\nworld!")

        assert result == EditResult(
            end_location=(3, 6),
            replaced_text="",
        )

        # The insert happens at the cursor (default location)
        # Offset is maintained - we inserted 1 line so cursor shifts
        # down 1 line, and along by the length of the last insert line.
        assert text_area.cursor_location == (3, 6)
        expected_content = """\
I must not fear.
Fear is the mind-killer.
Fear Hello,
world!is the little-death that brings total obliteration.
I will face my fear.
"""
        assert text_area.text == expected_content


async def test_replace_multiline_text():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        # replace "Fear is the mind-killer\nFear is the little death...\n"
        # with "Hello,\nworld!\n"
        result = text_area.replace("Hello,\nworld!\n", start=(1, 0), end=(3, 0))
        expected_replaced_text = """\
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
"""
        assert result == EditResult(
            end_location=(3, 0),
            replaced_text=expected_replaced_text,
        )

        expected_content = """\
I must not fear.
Hello,
world!
I will face my fear.
"""
        assert text_area.selection == Selection.cursor((0, 0))  # cursor didnt move
        assert text_area.text == expected_content


async def test_replace_multiline_text_maintain_selection():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # To begin with, the user selects the word "face"
        text_area.selection = Selection((3, 7), (3, 11))
        assert text_area.selected_text == "face"

        # Text is inserted via the API in a way that shifts
        # the start and end locations of the word "face" in
        # both the horizontal and vertical directions.
        text_area.replace(
            "Hello,\nworld!\n123\n456",
            start=(1, 0),
            end=(3, 0),
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


async def test_delete_within_line():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((0, 11), (0, 15))
        assert text_area.selected_text == "fear"

        # Delete some text before the selection location.
        result = text_area.delete((0, 6), (0, 10))

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


async def test_delete_within_line_dont_maintain_offset():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.delete((0, 6), (0, 10), maintain_selection_offset=False)
    expected_text = """\
I must fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
"""
    assert text_area.selection == Selection.cursor((0, 6))  # cursor moved
    assert text_area.text == expected_text


async def test_delete_multiple_lines_selection_above():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # User has selected text on the first line...
        text_area.selection = Selection((0, 2), (0, 6))
        assert text_area.selected_text == "must"

        # Some lines below are deleted...
        result = text_area.delete((1, 0), (3, 0))

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


async def test_delete_empty_document():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("")
        result = text_area.delete((0, 0), (1, 0))
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


@pytest.mark.parametrize(
    "select_from,select_to",
    [
        [(0, 3), (2, 1)],
        [(2, 1), (0, 3)],  # Ensuring independence from selection direction.
    ],
)
async def test_insert_text_multiline_selection_top(select_from, select_to):
    """
    An example to attempt to explain what we're testing here...

    X = edit range, * = character in TextArea, S = selection

    *********XX
    XXXXX***SSS
    SSSSSSSSSSS
    SSSS*******

    If an edit happens at XXXX, we need to ensure that the SSS on the
    same line is adjusted appropriately so that it's still highlighting
    the same characters as before.
    """
    app = TextAreaApp()
    async with app.run_test():
        # ABCDE
        # FGHIJ
        # KLMNO
        # PQRST
        # UVWXY
        # Z
        text_area = app.query_one(TextArea)
        text_area.load_text(SIMPLE_TEXT)
        text_area.selection = Selection(select_from, select_to)

        # Check what text is selected.
        expected_selected_text = "DE\nFGHIJ\nK"
        assert text_area.selected_text == expected_selected_text

        result = text_area.replace(
            "Hello",
            start=(0, 0),
            end=(0, 2),
        )

        assert result == EditResult(end_location=(0, 5), replaced_text="AB")

        # The edit range has grown from width 2 to width 5, so the
        # top line of the selection was adjusted (column+=3) such that the
        # same characters are highlighted:
        # ... the selection is not changed after programmatic insert
        # ... the same text is selected as before.
        assert text_area.selected_text == expected_selected_text

        # The resulting text in the TextArea is correct.
        assert text_area.text == "HelloCDE\nFGHIJ\nKLMNO\nPQRST\nUVWXY\nZ\n"


@pytest.mark.parametrize(
    "select_from,select_to",
    [
        [(0, 3), (2, 5)],
        [(2, 5), (0, 3)],  # Ensuring independence from selection direction.
    ],
)
async def test_insert_text_multiline_selection_bottom(select_from, select_to):
    """
    The edited text is within the selected text on the bottom line
    of the selection. The bottom of the selection should be adjusted
    such that any text that was previously selected is still selected.
    """
    app = TextAreaApp()
    async with app.run_test():
        # ABCDE
        # FGHIJ
        # KLMNO
        # PQRST
        # UVWXY
        # Z

        text_area = app.query_one(TextArea)
        text_area.load_text(SIMPLE_TEXT)
        text_area.selection = Selection(select_from, select_to)

        # Check what text is selected.
        assert text_area.selected_text == "DE\nFGHIJ\nKLMNO"

        result = text_area.replace(
            "*",
            start=(2, 0),
            end=(2, 3),
        )
        assert result == EditResult(end_location=(2, 1), replaced_text="KLM")

        # The 'NO' from the selection is still available on the
        # bottom selection line, however the 'KLM' is replaced
        # with '*'. Since 'NO' is still available, it's maintained
        # within the selection.
        assert text_area.selected_text == "DE\nFGHIJ\n*NO"

        # The resulting text in the TextArea is correct.
        # 'KLM' replaced with '*'
        assert text_area.text == "ABCDE\nFGHIJ\n*NO\nPQRST\nUVWXY\nZ\n"


async def test_delete_fully_within_selection():
    """User-facing selection should be best-effort adjusted when a programmatic
    replacement is made to the document."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = Selection((0, 2), (0, 7))
        assert text_area.selected_text == "23456"

        result = text_area.delete((0, 4), (0, 6))
        assert result == EditResult(
            replaced_text="45",
            end_location=(0, 4),
        )
        # We deleted 45, but the other characters are still available
        assert text_area.selected_text == "236"
        assert text_area.text == "01236789"


async def test_replace_fully_within_selection():
    """Adjust the selection when a replacement happens inside it."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = Selection((0, 2), (0, 7))
        assert text_area.selected_text == "23456"

        result = text_area.replace("XX", start=(0, 2), end=(0, 5))
        assert result == EditResult(
            replaced_text="234",
            end_location=(0, 4),
        )
        assert text_area.selected_text == "XX56"


async def test_text_setter():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        new_text = "hello\nworld\n"
        text_area.text = new_text
        assert text_area.text == new_text


async def test_edits_on_read_only_mode():
    """API edits should still be permitted on read-only mode."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.text = "0123456789"
        text_area.read_only = True

        text_area.replace("X", (0, 1), (0, 5))
        assert text_area.text == "0X56789"

        text_area.insert("X")
        assert text_area.text == "X0X56789"

        text_area.delete((0, 0), (0, 2))
        assert text_area.text == "X56789"
