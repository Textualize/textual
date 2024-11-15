import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

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


async def test_default_selection():
    """The cursor starts at (0, 0) in the document."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.selection == Selection.cursor((0, 0))


async def test_cursor_location_get():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((1, 1), (2, 2))
        assert text_area.cursor_location == (2, 2)


async def test_cursor_location_set():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        target = (1, 2)
        text_area.cursor_location = target
        assert text_area.selection == Selection.cursor(target)


async def test_cursor_location_set_while_selecting():
    """If you set the cursor_location while a selection is in progress,
    the start/anchor point of the selection will remain where it is."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((0, 0), (0, 2))
        target = (1, 2)
        text_area.cursor_location = target
        assert text_area.selection == Selection((0, 0), target)


async def test_move_cursor_select():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((1, 1), (2, 2))
        text_area.move_cursor((2, 3), select=True)
        assert text_area.selection == Selection((1, 1), (2, 3))


async def test_move_cursor_relative():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        text_area.move_cursor_relative(rows=1, columns=2)
        assert text_area.selection == Selection.cursor((1, 2))

        text_area.move_cursor_relative(rows=-1, columns=-2)
        assert text_area.selection == Selection.cursor((0, 0))

        text_area.move_cursor_relative(rows=1000, columns=1000)
        assert text_area.selection == Selection.cursor((4, 0))


async def test_selected_text_forward():
    """Selecting text from top to bottom results in the correct selected_text."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((0, 0), (2, 0))
        assert (
            text_area.selected_text
            == """\
I must not fear.
Fear is the mind-killer.
"""
        )


async def test_selected_text_backward():
    """Selecting text from bottom to top results in the correct selected_text."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((2, 0), (0, 0))
        assert (
            text_area.selected_text
            == """\
I must not fear.
Fear is the mind-killer.
"""
        )


async def test_selected_text_multibyte():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("こんにちは")
        text_area.selection = Selection((0, 1), (0, 3))
        assert text_area.selected_text == "んに"


async def test_selection_clamp():
    """When you set the selection reactive, it's clamped to within the document bounds."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((99, 99), (100, 100))
        assert text_area.selection == Selection(start=(4, 0), end=(4, 0))


@pytest.mark.parametrize(
    "start,end",
    [
        ((0, 0), (0, 0)),
        ((0, 4), (0, 3)),
        ((1, 0), (0, 16)),
    ],
)
async def test_get_cursor_left_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor(start)
        assert text_area.get_cursor_left_location() == end


@pytest.mark.parametrize(
    "start,end",
    [
        ((0, 0), (0, 1)),
        ((0, 16), (1, 0)),
        ((3, 20), (4, 0)),
        ((4, 0), (4, 0)),
    ],
)
async def test_get_cursor_right_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor(start)
        assert text_area.get_cursor_right_location() == end


@pytest.mark.parametrize(
    "start,end",
    [
        ((0, 4), (0, 0)),  # jump to start
        ((1, 2), (0, 2)),  # go to column above
        ((2, 56), (1, 24)),  # snap to end of row above
    ],
)
async def test_get_cursor_up_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor(start)
        # This is required otherwise the cursor will snap back to the
        # last location navigated to (0, 0)
        text_area.record_cursor_width()
        assert text_area.get_cursor_up_location() == end


@pytest.mark.parametrize(
    "start,end",
    [
        ((3, 4), (4, 0)),  # jump to end
        ((1, 2), (2, 2)),  # go to column above
        ((2, 56), (3, 20)),  # snap to end of row below
    ],
)
async def test_get_cursor_down_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.move_cursor(start)
        # This is required otherwise the cursor will snap back to the
        # last location navigated to (0, 0)
        text_area.record_cursor_width()
        assert text_area.get_cursor_down_location() == end


@pytest.mark.parametrize(
    "start,end",
    [
        ((0, 0), (0, 0)),
        ((0, 1), (0, 0)),
        ((0, 2), (0, 0)),
        ((0, 3), (0, 0)),
        ((0, 4), (0, 3)),
        ((0, 5), (0, 3)),
        ((0, 6), (0, 3)),
        ((0, 7), (0, 3)),
        ((0, 10), (0, 7)),
        ((1, 0), (0, 10)),
        ((1, 2), (1, 0)),
        ((1, 4), (1, 0)),
        ((1, 7), (1, 4)),
        ((1, 8), (1, 7)),
        ((1, 13), (1, 11)),
        ((1, 14), (1, 11)),
    ],
)
async def test_cursor_word_left_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("AB CD  EFG\n    HI\tJK  LM ")
        text_area.move_cursor(start)
        assert text_area.get_cursor_word_left_location() == end


@pytest.mark.parametrize(
    "start,end",
    [
        ((0, 0), (0, 2)),
        ((0, 1), (0, 2)),
        ((0, 2), (0, 5)),
        ((0, 3), (0, 5)),
        ((0, 4), (0, 5)),
        ((0, 5), (0, 10)),
        ((0, 6), (0, 10)),
        ((0, 7), (0, 10)),
        ((0, 10), (1, 0)),
        ((1, 0), (1, 6)),
        ((1, 2), (1, 6)),
        ((1, 4), (1, 6)),
        ((1, 7), (1, 9)),
        ((1, 8), (1, 9)),
        ((1, 13), (1, 14)),
        ((1, 14), (1, 14)),
    ],
)
async def test_cursor_word_right_location(start, end):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text("AB CD  EFG\n    HI\tJK  LM ")
        text_area.move_cursor(start)
        assert text_area.get_cursor_word_right_location() == end


@pytest.mark.parametrize(
    "content,expected_selection",
    [
        ("123\n456\n789", Selection((0, 0), (2, 3))),
        ("123\n456\n789\n", Selection((0, 0), (3, 0))),
        ("", Selection((0, 0), (0, 0))),
    ],
)
async def test_select_all(content, expected_selection):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text(content)

        text_area.select_all()

        assert text_area.selection == expected_selection


@pytest.mark.parametrize(
    "index,content,expected_selection",
    [
        (1, "123\n456\n789\n", Selection((1, 0), (1, 3))),
        (2, "123\n456\n789\n", Selection((2, 0), (2, 3))),
        (3, "123\n456\n789\n", Selection((3, 0), (3, 0))),
        (1000, "123\n456\n789\n", Selection.cursor((0, 0))),
        (0, "", Selection((0, 0), (0, 0))),
    ],
)
async def test_select_line(index, content, expected_selection):
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.load_text(content)

        text_area.select_line(index)

        assert text_area.selection == expected_selection


async def test_cursor_screen_offset_and_terminal_cursor_position_update():
    class TextAreaCursorScreenOffset(App):
        def compose(self) -> ComposeResult:
            yield TextArea.code_editor("abc\ndef")

    app = TextAreaCursorScreenOffset()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        assert app.cursor_position == (5, 1)

        text_area.cursor_location = (1, 1)

        assert text_area.cursor_screen_offset == (6, 2)

        # Also ensure that this update has been reported back to the app
        # for the benefit of IME/emoji popups.
        assert app.cursor_position == (6, 2)


async def test_cursor_screen_offset_and_terminal_cursor_position_scrolling():
    class TextAreaCursorScreenOffset(App):
        def compose(self) -> ComposeResult:
            yield TextArea.code_editor("AB\nAB\nAB\nAB\nAB\nAB\n")

    app = TextAreaCursorScreenOffset()
    async with app.run_test(size=(80, 2)) as pilot:
        text_area = app.query_one(TextArea)

        assert app.cursor_position == (5, 1)

        text_area.cursor_location = (5, 0)
        await pilot.pause()

        assert text_area.cursor_screen_offset == (5, 1)
        assert app.cursor_position == (5, 1)


async def test_mouse_selection_with_tab_characters():
    """Regression test for https://github.com/Textualize/textual/issues/5212"""

    class TextAreaTabsApp(App):
        def compose(self) -> ComposeResult:
            yield TextArea(soft_wrap=False, text="\t\t")

    app = TextAreaTabsApp()
    async with app.run_test() as pilot:
        text_area = pilot.app.query_one(TextArea)
        expected_selection = Selection((0, 0), (0, 0))
        assert text_area.selection == expected_selection

        await pilot.mouse_down(text_area, offset=(2, 1))
        await pilot.hover(text_area, offset=(3, 1))

        assert text_area.selection == expected_selection
