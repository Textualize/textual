from textual.app import App, ComposeResult
from textual.document._document import Selection
from textual.geometry import Offset
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


def test_default_selection():
    """The cursor starts at (0, 0) in the document."""
    text_area = TextArea()
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
        text_area.selection = Selection((1, 1), (2, 2))
        text_area.cursor_location = (2, 3)
        assert text_area.selection == Selection((1, 1), (2, 3))


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


async def test_selection_clamp():
    """When you set the selection reactive, it's clamped to within the document bounds."""
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((99, 99), (100, 100))
        assert text_area.selection == Selection(start=(4, 0), end=(4, 0))


async def test_mouse_click():
    """When you click the TextArea, the cursor moves to the expected location."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(TextArea, Offset(x=5, y=2))
        assert text_area.selection == Selection.cursor((2, 2))


async def test_mouse_click_clamp_from_right():
    """When you click to the right of the document bounds, the cursor is clamped
    to within the document bounds."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(TextArea, Offset(x=8, y=20))
        assert text_area.selection == Selection.cursor((4, 0))


async def test_mouse_click_gutter_clamp():
    """When you click the gutter, it selects the start of the line."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(TextArea, Offset(x=0, y=3))
        assert text_area.selection == Selection.cursor((3, 0))


async def test_cursor_selection_right():
    """When you press shift+right the selection is updated correctly."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.press(*["shift+right"] * 3)
        assert text_area.selection == Selection((0, 0), (0, 3))


async def test_cursor_selection_right_to_previous_line():
    """When you press shift+right resulting in the cursor moving to the next line,
    the selection is updated correctly."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.selection = Selection.cursor((0, 15))
        await pilot.press(*["shift+right"] * 4)
        assert text_area.selection == Selection((0, 15), (1, 2))


async def test_cursor_selection_left():
    """When you press shift+left the selection is updated correctly."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.selection = Selection.cursor((2, 5))
        await pilot.press(*["shift+left"] * 3)
        assert text_area.selection == Selection((2, 5), (2, 2))


async def test_cursor_selection_left_to_previous_line():
    """When you press shift+left resulting in the cursor moving back to the previous line,
    the selection is updated correctly."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        text_area.selection = Selection.cursor((2, 2))
        await pilot.press(*["shift+left"] * 3)

        # The cursor jumps up to the end of the line above.
        end_of_previous_line = len(TEXT.splitlines()[1])
        assert text_area.selection == Selection((2, 2), (1, end_of_previous_line))
