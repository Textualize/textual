import pytest

from textual.app import App, ComposeResult
from textual.document._document import Selection
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
    text_area = TextArea()
    assert text_area.selection == Selection.cursor((0, 0))


# def test_selection_modified():
#     app = TextAreaApp()
#     async with app.run_test():
#         text_area = app.query_one(TextArea)


async def test_selected_text_forward():
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
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.selection = Selection((99, 99), (100, 100))
        assert text_area.selection == Selection(start=(4, 0), end=(4, 0))


async def test_mouse_selection():
    # TODO: Wednesday.
    pass
