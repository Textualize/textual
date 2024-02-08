import pytest

from textual.app import App, ComposeResult
from textual.pilot import Pilot
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

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
        self.text_area = TextArea(SIMPLE_TEXT)
        yield self.text_area


@pytest.fixture
async def pilot():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        yield pilot


@pytest.fixture
async def text_area(pilot):
    return pilot.app.text_area


async def test_simple_undo_redo(pilot, text_area: TextArea):
    text_area.insert("123", (0, 0))

    assert text_area.text == "123" + SIMPLE_TEXT
    text_area.undo()
    assert text_area.text == SIMPLE_TEXT
    text_area.redo()
    assert text_area.text == "123" + SIMPLE_TEXT


async def test_undo_selection_retained(pilot: Pilot, text_area: TextArea):
    # Select a range of text and press backspace.
    text_area.selection = Selection((0, 0), (2, 3))
    await pilot.press("backspace")
    assert text_area.text == "NO\nPQRST\nUVWXY\nZ\n"
    assert text_area.selection == Selection.cursor((0, 0))

    # Undo the deletion - the text comes back, and the selection is restored.
    text_area.undo()
    assert text_area.selection == Selection((0, 0), (2, 3))
    assert text_area.text == SIMPLE_TEXT

    # Redo the deletion - the text is gone again. The selection goes to the post-delete location.
    text_area.redo()
    assert text_area.text == "NO\nPQRST\nUVWXY\nZ\n"
    assert text_area.selection == Selection.cursor((0, 0))


async def test_undo_checkpoint_created_on_cursor_move(
    pilot: Pilot, text_area: TextArea
):
    # Characters are inserted on line 0 and 1.
    checkpoint_one = text_area.text
    checkpoint_one_selection = text_area.selection
    await pilot.press("1")  # Added to initial batch.

    # This cursor movement ensures a new checkpoint is created.
    post_insert_one_location = text_area.selection
    await pilot.press("down")

    checkpoint_two = text_area.text
    checkpoint_two_selection = text_area.selection
    await pilot.press("2")  # Added to new batch.

    checkpoint_three = text_area.text
    checkpoint_three_selection = text_area.selection

    # Going back to checkpoint two
    text_area.undo()
    assert text_area.text == checkpoint_two
    assert text_area.selection == checkpoint_two_selection

    # Back again to checkpoint one (initial state)
    text_area.undo()
    assert text_area.text == checkpoint_one
    assert text_area.selection == checkpoint_one_selection

    # Redo to move forward to checkpoint two.
    text_area.redo()
    assert text_area.text == checkpoint_two
    assert text_area.selection == post_insert_one_location

    # Redo to move forward to checkpoint three.
    text_area.redo()
    assert text_area.text == checkpoint_three
    assert text_area.selection == checkpoint_three_selection


async def test_undo_checkpoint_character_limit_reached(
    pilot: Pilot, text_area: TextArea
):
    pass  # TODO


async def test_redo_stack_cleared_on_edit(pilot: Pilot, text_area: TextArea):
    pass  # TODO:


async def test_inserts_not_batched_with_deletes(pilot: Pilot, text_area: TextArea):
    pass  # TODO


async def test_paste_is_an_isolated_batch(pilot: Pilot, text_area: TextArea):
    pass  # TODO


async def test_undo_redo_deletions_batched(pilot: Pilot, text_area: TextArea):
    text_area.selection = Selection((0, 2), (1, 2))

    # Perform a single delete of some selected text. It'll live in it's own
    # batch since it's a multi-line operation.
    await pilot.press("backspace")
    checkpoint_one = "ABHIJ\nKLMNO\nPQRST\nUVWXY\nZ\n"
    assert text_area.text == checkpoint_one
    assert text_area.selection == Selection.cursor((0, 2))

    # Pressing backspace a few times to delete more characters.
    await pilot.press("backspace", "backspace", "backspace")
    checkpoint_two = "HIJ\nKLMNO\nPQRST\nUVWXY\nZ\n"
    assert text_area.text == checkpoint_two
    assert text_area.selection == Selection.cursor((0, 0))

    # When we undo, the 3 deletions above should be batched, but not
    # the original deletion since it contains a newline character.
    text_area.undo()
    assert text_area.text == checkpoint_one
    assert text_area.selection == Selection.cursor((0, 2))

    # Undoing again restores us back to our initial text and selection.
    text_area.undo()
    assert text_area.text == SIMPLE_TEXT
    assert text_area.selection == Selection((0, 2), (1, 2))

    # At this point, the undo stack contains two items, so we can undo twice.

    # Redo to go back to checkpoint one.
    text_area.redo()
    assert text_area.text == checkpoint_one
    assert text_area.selection == Selection.cursor((0, 2))

    # Redo again to go back to checkpoint two
    text_area.redo()
    assert text_area.text == checkpoint_two
    assert text_area.selection == Selection.cursor((0, 0))

    # Redo again does nothing.
    text_area.redo()
    assert text_area.text == checkpoint_two
    assert text_area.selection == Selection.cursor((0, 0))
