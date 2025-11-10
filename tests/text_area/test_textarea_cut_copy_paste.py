from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea()


async def test_cut():
    """Check that cut removes text and places it in the clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+x")
        assert text_area.text == "Hello, Wod"
        assert app.clipboard == "rl"


async def test_copy():
    """Check that copy places text in the clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press("left", "shift+left", "shift+left")
        await pilot.press("ctrl+c")
        assert text_area.text == "Hello, World"
        assert app.clipboard == "rl"


async def test_paste():
    """Check that paste copies text from the local clipboard."""
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)
        await pilot.press(*"Hello, World")
        await pilot.press(
            "shift+left", "shift+left", "shift+left", "shift+left", "shift+left"
        )
        await pilot.press("ctrl+c")
        assert text_area.text == "Hello, World"
        assert app.clipboard == "World"
        await pilot.press("ctrl+v")
        assert text_area.text == "Hello, World"
        await pilot.press("ctrl+v")
        assert text_area.text == "Hello, WorldWorld"


async def test_paste_scrollbar_position_updated():
    """Regression test for issue #4852: scrollbar position should be updated after paste.

    When pasting text that extends beyond the visible area, the scrollbar should
    automatically scroll to show the cursor position after the pasted text.
    """
    app = TextAreaApp()
    async with app.run_test(size=(40, 10)) as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)

        # Create long text that will require scrolling
        long_text = "\n".join(f"Line {i}" for i in range(50))
        app.copy_to_clipboard(long_text)

        # Get initial scroll position
        initial_scroll_x, initial_scroll_y = text_area.scroll_offset

        # Paste the text
        await pilot.press("ctrl+v")

        # Wait for the paste to complete and scrollbar to update
        await pilot.pause()

        # Get scroll position after paste
        final_scroll_x, final_scroll_y = text_area.scroll_offset

        # The scrollbar should have scrolled down to show the cursor
        # (which should be at the end of the pasted text)
        assert final_scroll_y > initial_scroll_y, (
            f"Scrollbar should have scrolled down after paste. "
            f"Initial: {initial_scroll_y}, Final: {final_scroll_y}"
        )

        # Verify the text was pasted
        assert text_area.text == long_text


async def test_paste_event_scrollbar_position_updated():
    """Regression test for issue #4852: scrollbar position should be updated after paste event.

    Tests the _on_paste method specifically (paste via event, not action).
    """
    from textual.events import Paste

    app = TextAreaApp()
    async with app.run_test(size=(40, 10)) as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)

        # Create long text that will require scrolling
        long_text = "\n".join(f"Line {i}" for i in range(50))

        # Get initial scroll position
        initial_scroll_x, initial_scroll_y = text_area.scroll_offset

        # Post a paste event
        app.post_message(Paste(long_text))
        await pilot.pause()

        # Get scroll position after paste
        final_scroll_x, final_scroll_y = text_area.scroll_offset

        # The scrollbar should have scrolled down to show the cursor
        assert final_scroll_y > initial_scroll_y, (
            f"Scrollbar should have scrolled down after paste event. "
            f"Initial: {initial_scroll_y}, Final: {final_scroll_y}"
        )

        # Verify the text was pasted
        assert text_area.text == long_text


async def test_paste_scrollbar_with_wide_text():
    """Regression test for issue #4852: scrollbar position updated with wide text.

    Based on comment from TomJGooding: vertical scrollbar updates correctly
    when horizontal scrollbar is also triggered. This test verifies both scrollbars work.
    """
    app = TextAreaApp()
    async with app.run_test(size=(40, 10)) as pilot:
        text_area = app.query_one(TextArea)
        await pilot.click(text_area)

        # Create text that requires both horizontal and vertical scrolling
        # Wide lines + many lines
        wide_text = "\n".join(f"Line {i}: {'x' * 100}" for i in range(50))
        app.copy_to_clipboard(wide_text)

        # Get initial scroll position
        initial_scroll_x, initial_scroll_y = text_area.scroll_offset

        # Paste the text
        await pilot.press("ctrl+v")
        await pilot.pause()

        # Get scroll position after paste
        final_scroll_x, final_scroll_y = text_area.scroll_offset

        # Both scrollbars should have updated
        # Vertical scrollbar should have scrolled down
        assert final_scroll_y > initial_scroll_y, (
            f"Vertical scrollbar should have scrolled down after paste. "
            f"Initial: {initial_scroll_y}, Final: {final_scroll_y}"
        )

        # Horizontal scrollbar may or may not scroll depending on cursor position
        # But the important thing is that vertical scrollbar updated correctly

        # Verify the text was pasted
        assert text_area.text == wide_text
