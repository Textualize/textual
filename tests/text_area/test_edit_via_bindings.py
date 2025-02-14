"""Tests some edits using the keyboard.

All tests in this module should press keys on the keyboard which edit the document,
and check that the document content is updated as expected, as well as the cursor
location.

Note that more extensive testing for editing is done at the Document level.
"""

import pytest

from textual.app import App, ComposeResult
from textual.events import Paste
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
        text_area = TextArea.code_editor()
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


@pytest.mark.parametrize(
    "content,cursor_column,cursor_destination",
    [
        ("", 0, 4),
        ("x", 0, 4),
        ("x", 1, 4),
        ("xxx", 3, 4),
        ("xxxx", 4, 8),
        ("xxxxx", 5, 8),
        ("xxxxxx", 6, 8),
        ("💩", 1, 3),
        ("💩💩", 2, 6),
    ],
)
async def test_tab_with_spaces_goes_to_tab_stop(
    content, cursor_column, cursor_destination
):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.indent_width = 4
        text_area.load_text(content)
        text_area.cursor_location = (0, cursor_column)

        await pilot.press("tab")

        assert text_area.cursor_location[1] == cursor_destination


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
    "selection,expected_result,expected_clipboard,cursor_end_location",
    [
        (Selection.cursor((0, 0)), "", "0123456789", (0, 0)),
        (Selection.cursor((0, 4)), "", "0123456789", (0, 0)),
        (Selection.cursor((0, 10)), "", "0123456789", (0, 0)),
        (Selection((0, 2), (0, 4)), "01456789", "23", (0, 2)),
        (Selection((0, 4), (0, 2)), "01456789", "23", (0, 2)),
    ],
)
async def test_cut(selection, expected_result, expected_clipboard, cursor_end_location):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("0123456789")
        text_area.selection = selection

        await pilot.press("ctrl+x")

        assert text_area.selection == Selection.cursor(cursor_end_location)
        assert text_area.text == expected_result
        assert app.clipboard == expected_clipboard


@pytest.mark.parametrize(
    "selection,expected_result",
    [
        # Cursors
        (Selection.cursor((0, 0)), "345\n678\n9\n"),
        (Selection.cursor((0, 2)), "345\n678\n9\n"),
        (Selection.cursor((3, 1)), "012\n345\n678\n"),
        (Selection.cursor((4, 0)), "012\n345\n678\n9\n"),
        # Selections
        (Selection((1, 1), (1, 2)), "012\n35\n678\n9\n"),
        (Selection((1, 2), (2, 1)), "012\n3478\n9\n"),
    ],
)
async def test_cut_multiline_document(selection, expected_result):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.load_text("012\n345\n678\n9\n")
        text_area.selection = selection

        await pilot.press("ctrl+x")

        cursor_row, cursor_column = text_area.cursor_location
        assert text_area.selection == Selection.cursor((cursor_row, cursor_column))
        assert text_area.text == expected_result


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

        await pilot.press("ctrl+shift+k")

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

        await pilot.press("ctrl+shift+k")

        cursor_row, cursor_column = text_area.cursor_location
        assert text_area.selection == Selection.cursor((cursor_row, cursor_column))
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


@pytest.mark.parametrize(
    "binding",
    [
        "enter",
        "backspace",
        "ctrl+u",
        "ctrl+f",
        "ctrl+w",
        "ctrl+k",
        "ctrl+x",
        "space",
        "1",
        "tab",
    ],
)
async def test_edit_read_only_mode_does_nothing(binding):
    """Try out various key-presses and bindings and ensure they don't alter
    the document when read_only=True."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.read_only = True
        selection = Selection.cursor((0, 2))
        text_area.selection = selection

        await pilot.press(binding)

        assert text_area.text == TEXT
        assert text_area.selection == selection


@pytest.mark.parametrize(
    "selection",
    [
        Selection(start=(1, 0), end=(3, 0)),
        Selection(start=(3, 0), end=(1, 0)),
    ],
)
async def test_replace_lines_with_fewer_lines(selection):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.text = SIMPLE_TEXT
        text_area.selection = selection

        await pilot.press("a")

        expected_text = """\
ABCDE
aPQRST
UVWXY
Z"""
        assert text_area.text == expected_text
        assert text_area.selection == Selection.cursor((1, 1))


@pytest.mark.parametrize(
    "selection",
    [
        Selection(start=(1, 0), end=(3, 0)),
        Selection(start=(3, 0), end=(1, 0)),
    ],
)
async def test_paste(selection):
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.text = SIMPLE_TEXT
        text_area.selection = selection

        app.post_message(Paste("a"))
        await pilot.pause()

        expected_text = """\
ABCDE
aPQRST
UVWXY
Z"""
        assert text_area.text == expected_text
        assert text_area.selection == Selection.cursor((1, 1))


async def test_paste_read_only_does_nothing():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.read_only = True

        app.post_message(Paste("hello"))
        await pilot.pause()

        assert text_area.text == TEXT  # No change
