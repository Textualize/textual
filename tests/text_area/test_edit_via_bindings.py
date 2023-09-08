"""Tests some edits using the keyboard.

All tests in this module should press keys on the keyboard which edit the document,
and check that the document content is updated as expected, as well as the cursor
location.

Note that more extensive testing for editing is done at the Document level.
"""
import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

TEXT = """I must not fear.
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
Z"""


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


@pytest.mark.parametrize(
    "key,selection",
    [
        ("delete", Selection((1, 2), (3, 4))),
        ("delete", Selection((3, 4), (1, 2))),
        ("backspace", Selection((1, 2), (3, 4))),
        ("backspace", Selection((3, 4), (1, 2))),
    ],
)
async def test_deletion_with_non_empty_selection(key, selection):
    """When there's a selection, pressing backspace or delete should delete everything
    that is selected and reset the selection to a cursor at the appropriate location."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text(SIMPLE_TEXT)
        text_area.selection = selection
        await pilot.press(key)
        assert text_area.selection == Selection.cursor((1, 2))
        assert (
            text_area.text
            == """\
ABCDE
FGT
UVWXY
Z"""
        )


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


@pytest.mark.parametrize(
    "selection,expected_result",
    [
        (Selection.cursor((0, 0)), ""),
        (Selection.cursor((0, 4)), ""),
        (Selection.cursor((0, 10)), ""),
        (Selection((0, 2), (0, 4)), ""),
        (Selection((0, 4), (0, 2)), ""),
    ],
)
async def test_delete_line(selection, expected_result):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = selection

        await pilot.press("ctrl+x")

        assert text_area.selection == Selection.cursor((0, 0))
        assert text_area.text == expected_result


@pytest.mark.parametrize(
    "selection,expected_result",
    [
        # Cursors
        (Selection.cursor((0, 0)), "345\n678\n9\n"),
        (Selection.cursor((0, 2)), "345\n678\n9\n"),
        (Selection.cursor((3, 1)), "012\n345\n678\n"),
        (Selection.cursor((4, 0)), "012\n345\n678\n9\n"),
        # Selections
        (Selection((1, 1), (1, 2)), "012\n678\n9\n"),  # non-empty single line selection
        (Selection((1, 2), (2, 1)), "012\n9\n"),  # delete lines selection touches
        (
            Selection((1, 2), (3, 0)),
            "012\n9\n",
        ),  # cursor at column 0 of line 3, should not be deleted!
        (
            Selection((3, 0), (1, 2)),
            "012\n9\n",
        ),  # opposite direction
        (Selection((0, 0), (4, 0)), ""),  # delete all lines
    ],
)
async def test_delete_line_multiline_document(selection, expected_result):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("012\n345\n678\n9\n")
        text_area.selection = selection

        await pilot.press("ctrl+x")

        cursor_row, _ = text_area.cursor_location
        assert text_area.selection == Selection.cursor((cursor_row, 0))
        assert text_area.text == expected_result


@pytest.mark.parametrize(
    "selection,expected_result",
    [
        # Cursors
        (Selection.cursor((0, 0)), ""),
        (Selection.cursor((0, 5)), "01234"),
        (Selection.cursor((0, 9)), "012345678"),
        (Selection.cursor((0, 10)), "0123456789"),
        # Selections
        (Selection((0, 0), (0, 9)), "012345678"),
        (Selection((0, 0), (0, 10)), "0123456789"),
        (Selection((0, 2), (0, 5)), "01234"),
        (Selection((0, 5), (0, 2)), "01"),
    ],
)
async def test_delete_to_end_of_line(selection, expected_result):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = selection

        await pilot.press("ctrl+k")

        assert text_area.selection == Selection.cursor(selection.end)
        assert text_area.text == expected_result


@pytest.mark.parametrize(
    "selection,expected_result",
    [
        # Cursors
        (Selection.cursor((0, 0)), "0123456789"),
        (Selection.cursor((0, 5)), "56789"),
        (Selection.cursor((0, 9)), "9"),
        (Selection.cursor((0, 10)), ""),
        # Selections
        (Selection((0, 0), (0, 9)), "9"),
        (Selection((0, 0), (0, 10)), ""),
        (Selection((0, 2), (0, 5)), "56789"),
        (Selection((0, 5), (0, 2)), "23456789"),
    ],
)
async def test_delete_to_start_of_line(selection, expected_result):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = selection

        await pilot.press("ctrl+u")

        assert text_area.selection == Selection.cursor((0, 0))
        assert text_area.text == expected_result


@pytest.mark.parametrize(
    "selection,expected_result,final_selection",
    [
        (Selection.cursor((0, 0)), "  012 345 6789", Selection.cursor((0, 0))),
        (Selection.cursor((0, 4)), "  2 345 6789", Selection.cursor((0, 2))),
        (Selection.cursor((0, 5)), "   345 6789", Selection.cursor((0, 2))),
        (
            Selection.cursor((0, 6)),
            "  345 6789",
            Selection.cursor((0, 2)),
        ),
        (Selection.cursor((0, 14)), "  012 345 ", Selection.cursor((0, 10))),
        # When there's a selection and you "delete word left", it just deletes the selection
        (Selection((0, 4), (0, 11)), "  01789", Selection.cursor((0, 4))),
    ],
)
async def test_delete_word_left(selection, expected_result, final_selection):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("  012 345 6789")
        text_area.selection = selection

        await pilot.press("ctrl+w")

        assert text_area.text == expected_result
        assert text_area.selection == final_selection


@pytest.mark.parametrize(
    "selection,expected_result,final_selection",
    [
        (Selection.cursor((0, 0)), "\t012 \t 345\t6789", Selection.cursor((0, 0))),
        (Selection.cursor((0, 4)), "\t \t 345\t6789", Selection.cursor((0, 1))),
        (Selection.cursor((0, 5)), "\t\t 345\t6789", Selection.cursor((0, 1))),
        (
            Selection.cursor((0, 6)),
            "\t 345\t6789",
            Selection.cursor((0, 1)),
        ),
        (Selection.cursor((0, 15)), "\t012 \t 345\t", Selection.cursor((0, 11))),
        # When there's a selection and you "delete word left", it just deletes the selection
        (Selection((0, 4), (0, 11)), "\t0126789", Selection.cursor((0, 4))),
    ],
)
async def test_delete_word_left_with_tabs(selection, expected_result, final_selection):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("\t012 \t 345\t6789")
        text_area.selection = selection

        await pilot.press("ctrl+w")

        assert text_area.text == expected_result
        assert text_area.selection == final_selection


async def test_delete_word_left_to_start_of_line():
    """If no word boundary found when we 'delete word left', then
    the deletion happens to the start of the line."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123\n   456789")
        text_area.selection = Selection.cursor((1, 3))

        await pilot.press("ctrl+w")

        assert text_area.text == "0123\n456789"
        assert text_area.selection == Selection.cursor((1, 0))


async def test_delete_word_left_at_line_start():
    """If we're at the start of a line and we 'delete word left', the
    line merges with the line above (if possible)."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123\n   456789")
        text_area.selection = Selection.cursor((1, 0))

        await pilot.press("ctrl+w")

        assert text_area.text == "0123   456789"
        assert text_area.selection == Selection.cursor((0, 4))


@pytest.mark.parametrize(
    "selection,expected_result,final_selection",
    [
        (Selection.cursor((0, 0)), "012 345 6789", Selection.cursor((0, 0))),
        (Selection.cursor((0, 4)), "  01 345 6789", Selection.cursor((0, 4))),
        (Selection.cursor((0, 5)), "  012345 6789", Selection.cursor((0, 5))),
        (Selection.cursor((0, 14)), "  012 345 6789", Selection.cursor((0, 14))),
        # When non-empty selection, "delete word right" just deletes the selection
        (Selection((0, 4), (0, 11)), "  01789", Selection.cursor((0, 4))),
    ],
)
async def test_delete_word_right(selection, expected_result, final_selection):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("  012 345 6789")
        text_area.selection = selection

        await pilot.press("ctrl+f")

        assert text_area.text == expected_result
        assert text_area.selection == final_selection


async def test_delete_word_right_delete_to_end_of_line():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("01234\n56789")
        text_area.selection = Selection.cursor((0, 3))

        await pilot.press("ctrl+f")

        assert text_area.text == "012\n56789"
        assert text_area.selection == Selection.cursor((0, 3))


async def test_delete_word_right_at_end_of_line():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("01234\n56789")
        text_area.selection = Selection.cursor((0, 5))

        await pilot.press("ctrl+f")

        assert text_area.text == "0123456789"
        assert text_area.selection == Selection.cursor((0, 5))
