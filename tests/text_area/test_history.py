from __future__ import annotations

import dataclasses

import pytest

from textual.app import App, ComposeResult
from textual.events import Paste
from textual.widgets import TextArea
from textual.widgets.text_area import EditHistory, Selection

MAX_CHECKPOINTS = 5
SIMPLE_TEXT = """\
ABCDE
FGHIJ
KLMNO
PQRST
UVWXY
Z
"""


@dataclasses.dataclass
class TimeMockableEditHistory(EditHistory):
    mock_time: float | None = dataclasses.field(default=None, init=False)

    def _get_time(self) -> float:
        """Return the mocked time if it is set, otherwise use default behaviour."""
        if self.mock_time is None:
            return super()._get_time()
        return self.mock_time


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea()
        # Update the history object to a version that supports mocking the time.
        text_area.history = TimeMockableEditHistory(
            max_checkpoints=MAX_CHECKPOINTS,
            checkpoint_timer=2.0,
            checkpoint_max_characters=100,
        )
        self.text_area = text_area
        yield text_area


@pytest.fixture
async def pilot():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        yield pilot


@pytest.fixture
async def text_area(pilot):
    return pilot.app.text_area


async def test_simple_undo_redo():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.insert("123", (0, 0))

        assert text_area.text == "123"
        text_area.undo()
        assert text_area.text == ""
        text_area.redo()
        assert text_area.text == "123"


async def test_undo_selection_retained():
    # Select a range of text and press backspace.
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = SIMPLE_TEXT
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


async def test_undo_checkpoint_created_on_cursor_move():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = SIMPLE_TEXT
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


async def test_setting_text_property_resets_history():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        await pilot.press("1")

        # Programmatically setting text, which should invalidate the history
        text = "Hello, world!"
        text_area.text = text

        # The undo doesn't do anything, since we set the `text` property.
        text_area.undo()
        assert text_area.text == text


async def test_edits_batched_by_time():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        # The first "12" is batched since they happen within 2 seconds.
        text_area.history.mock_time = 0
        await pilot.press("1")

        text_area.history.mock_time = 1.0
        await pilot.press("2")

        # Since "3" appears 10 seconds later, it's in a separate batch.
        text_area.history.mock_time += 10.0
        await pilot.press("3")

        assert text_area.text == "123"

        text_area.undo()
        assert text_area.text == "12"

        text_area.undo()
        assert text_area.text == ""


async def test_undo_checkpoint_character_limit_reached():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        await pilot.press("1")
        # Since the insertion below is > 100 characters it goes to a new batch.
        text_area.insert("2" * 120)

        text_area.undo()
        assert text_area.text == "1"
        text_area.undo()
        assert text_area.text == ""


async def test_redo_with_no_undo_is_noop():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = SIMPLE_TEXT
        text_area.redo()
        assert text_area.text == SIMPLE_TEXT


async def test_undo_with_empty_undo_stack_is_noop():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = SIMPLE_TEXT
        text_area.undo()
        assert text_area.text == SIMPLE_TEXT


async def test_redo_stack_cleared_on_edit():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = ""
        await pilot.press("1")
        text_area.history.checkpoint()
        await pilot.press("2")
        text_area.history.checkpoint()
        await pilot.press("3")

        text_area.undo()
        text_area.undo()
        text_area.undo()
        assert text_area.text == ""
        assert text_area.selection == Selection.cursor((0, 0))

        # Redo stack has 3 edits in it now.
        await pilot.press("f")
        assert text_area.text == "f"
        assert text_area.selection == Selection.cursor((0, 1))

        # Redo stack is cleared because of the edit, so redo has no effect.
        text_area.redo()
        assert text_area.text == "f"
        assert text_area.selection == Selection.cursor((0, 1))
        text_area.redo()
        assert text_area.text == "f"
        assert text_area.selection == Selection.cursor((0, 1))


async def test_inserts_not_batched_with_deletes():
    # 3 batches here: __1___  ___________2____________  __3__

    app = TextAreaApp()

    async with app.run_test() as pilot:
        text_area = app.text_area
        await pilot.press(*"123", "backspace", "backspace", *"23")

        assert text_area.text == "123"

        # Undo batch 1: the "23" insertion.
        text_area.undo()
        assert text_area.text == "1"

        # Undo batch 2: the double backspace.
        text_area.undo()
        assert text_area.text == "123"

        # Undo batch 3: the "123" insertion.
        text_area.undo()
        assert text_area.text == ""


async def test_paste_is_an_isolated_batch():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        pilot.app.post_message(Paste("hello "))
        pilot.app.post_message(Paste("world"))
        await pilot.pause()

        assert text_area.text == "hello world"

        await pilot.press("!")

        # The insertion of "!" does not get batched with the paste of "world".
        text_area.undo()
        assert text_area.text == "hello world"

        text_area.undo()
        assert text_area.text == "hello "

        text_area.undo()
        assert text_area.text == ""


async def test_focus_creates_checkpoint():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        await pilot.press(*"123")
        text_area.has_focus = False
        text_area.has_focus = True
        await pilot.press(*"456")
        assert text_area.text == "123456"

        # Since we re-focused, a checkpoint exists between 123 and 456,
        # so when we use undo, only the 456 is removed.
        text_area.undo()
        assert text_area.text == "123"


async def test_undo_redo_deletions_batched():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        text_area.text = SIMPLE_TEXT
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

        # At this point, the undo stack contains two items, so we can redo twice.

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


async def test_max_checkpoints():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        assert len(text_area.history.undo_stack) == 0
        for index in range(MAX_CHECKPOINTS):
            # Press enter since that will ensure a checkpoint is created.
            await pilot.press("enter")

        assert len(text_area.history.undo_stack) == MAX_CHECKPOINTS
        await pilot.press("enter")
        # Ensure we don't go over the limit.
        assert len(text_area.history.undo_stack) == MAX_CHECKPOINTS


async def test_redo_stack():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        assert len(text_area.history.redo_stack) == 0
        await pilot.press("enter")
        await pilot.press(*"123")
        assert len(text_area.history.undo_stack) == 2
        assert len(text_area.history.redo_stack) == 0
        text_area.undo()
        assert len(text_area.history.undo_stack) == 1
        assert len(text_area.history.redo_stack) == 1
        text_area.undo()
        assert len(text_area.history.undo_stack) == 0
        assert len(text_area.history.redo_stack) == 2
        text_area.redo()
        assert len(text_area.history.undo_stack) == 1
        assert len(text_area.history.redo_stack) == 1
        text_area.redo()
        assert len(text_area.history.undo_stack) == 2
        assert len(text_area.history.redo_stack) == 0


async def test_backward_selection_undo_redo():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.text_area
        # Failed prior to https://github.com/Textualize/textual/pull/4352
        text_area.text = SIMPLE_TEXT
        text_area.selection = Selection((3, 2), (0, 0))

        await pilot.press("a")

        text_area.undo()
        await pilot.press("down", "down", "down", "down")

        assert text_area.text == SIMPLE_TEXT
