from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Log, RichLog


async def test_make_renderable_expand_tabs():
    # Regression test for https://github.com/Textualize/textual/issues/3007
    text_log = RichLog()
    renderable = text_log._make_renderable("\tfoo")
    assert isinstance(renderable, Text)
    assert renderable.plain == "        foo"


async def test_richlog_auto_scroll_respects_manual_scroll():
    """Regression test for https://github.com/Textualize/textual/issues/6311.

    When auto_scroll=True (default) and the user has scrolled up, new content
    must not force the view back to the bottom. Only new content written while
    the user is already at the bottom should auto-scroll.
    """
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield RichLog()

    async with TestApp().run_test(size=(80, 24)) as pilot:
        rich_log = pilot.app.query_one(RichLog)
        # Write enough lines to overflow the viewport
        for i in range(100):
            rich_log.write(f"Line {i}\n")
        await pilot.pause()

        # Now we're at the bottom — verify scroll_end
        assert rich_log.is_vertical_scroll_end

        # Scroll up manually
        rich_log.scroll_up(animate=False, immediate=True)
        rich_log.scroll_up(animate=False, immediate=True)
        rich_log.scroll_up(animate=False, immediate=True)
        rich_log.scroll_up(animate=False, immediate=True)
        rich_log.scroll_up(animate=False, immediate=True)
        await pilot.pause()
        assert not rich_log.is_vertical_scroll_end

        # Write more content — should NOT force scroll to bottom
        rich_log.write("New line while scrolled up\n")
        await pilot.pause()
        assert not rich_log.is_vertical_scroll_end, (
            "Writing to RichLog while scrolled up must not push view to bottom"
        )

        # Scroll back to bottom and write — should auto-scroll
        rich_log.scroll_end(animate=False)
        await pilot.pause()
        assert rich_log.is_vertical_scroll_end
        rich_log.write("Line after scroll to end\n")
        await pilot.pause()
        assert rich_log.is_vertical_scroll_end


async def test_log_auto_scroll_respects_manual_scroll():
    """Same as above for Log widget — both must behave consistently."""
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield Log()

    async with TestApp().run_test(size=(80, 24)) as pilot:
        log = pilot.app.query_one(Log)
        for i in range(100):
            log.write(f"Line {i}\n")
        await pilot.pause()

        assert log.is_vertical_scroll_end

        log.scroll_up(animate=False, immediate=True)
        log.scroll_up(animate=False, immediate=True)
        log.scroll_up(animate=False, immediate=True)
        log.scroll_up(animate=False, immediate=True)
        log.scroll_up(animate=False, immediate=True)
        await pilot.pause()
        assert not log.is_vertical_scroll_end

        log.write("New line while scrolled up\n")
        await pilot.pause()
        assert not log.is_vertical_scroll_end, (
            "Writing to Log while scrolled up must not push view to bottom"
        )

        log.scroll_end(animate=False)
        await pilot.pause()
        assert log.is_vertical_scroll_end
        log.write("Line after scroll to end\n")
        await pilot.pause()
        assert log.is_vertical_scroll_end
