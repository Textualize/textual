"""Tests for anchored scroll behavior."""

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


async def test_anchor_follows_new_content() -> None:
    """An anchored widget stays at the bottom as content grows."""

    class AnchorApp(App[None]):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="v"):
                for i in range(30):
                    yield Static(f"line {i}")

        def on_mount(self) -> None:
            self.query_one("#v", VerticalScroll).anchor()

    app = AnchorApp()
    async with app.run_test(size=(40, 10)) as pilot:
        v = app.query_one("#v", VerticalScroll)
        await pilot.pause()
        assert v.is_vertical_scroll_end

        v.mount(Static("line 30"))
        await pilot.pause()
        assert v.is_vertical_scroll_end
        assert v.is_anchored
        assert not v._anchor_released


async def test_anchor_released_when_scrolling_up() -> None:
    """Scrolling away from the bottom releases the anchor."""

    class AnchorApp(App[None]):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="v"):
                for i in range(30):
                    yield Static(f"line {i}")

        def on_mount(self) -> None:
            self.query_one("#v", VerticalScroll).anchor()

    app = AnchorApp()
    async with app.run_test(size=(40, 10)) as pilot:
        v = app.query_one("#v", VerticalScroll)
        await pilot.pause()
        max_before = v.max_scroll_y

        v.scroll_relative(y=-1, animate=False, immediate=True)
        await pilot.pause()
        assert v._anchor_released
        assert v.scroll_y < max_before

        v.mount(Static("line 30"))
        await pilot.pause()
        assert v.scroll_y < v.max_scroll_y


async def test_anchor_restored_when_scrolling_to_bottom() -> None:
    """Scrolling back to the bottom re-engages the anchor."""

    class AnchorApp(App[None]):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="v"):
                for i in range(30):
                    yield Static(f"line {i}")

        def on_mount(self) -> None:
            self.query_one("#v", VerticalScroll).anchor()

    app = AnchorApp()
    async with app.run_test(size=(40, 10)) as pilot:
        v = app.query_one("#v", VerticalScroll)
        await pilot.pause()

        v.scroll_relative(y=-1, animate=False, immediate=True)
        await pilot.pause()
        assert v._anchor_released

        v.scroll_end(immediate=True, animate=False)
        await pilot.pause()
        assert not v._anchor_released

        v.mount(Static("line 30"))
        await pilot.pause()
        assert v.is_vertical_scroll_end


async def test_anchor_restored_while_content_streams() -> None:
    """Reaching the bottom while content streams restores anchored scroll."""

    class AnchorStuck(App[None]):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="v"):
                for i in range(30):
                    yield Static(f"line {i}")

        def on_mount(self) -> None:
            self.query_one("#v", VerticalScroll).anchor()

    app = AnchorStuck()
    async with app.run_test(size=(40, 10)) as pilot:
        v = app.query_one("#v", VerticalScroll)
        await pilot.pause()

        v.scroll_relative(y=-1, animate=False, immediate=True)
        await pilot.pause()
        assert v._anchor_released

        v.scroll_end(immediate=True, animate=False)
        await pilot.pause()
        assert not v._anchor_released

        for i in range(5):
            v.mount(Static(f"line {30 + i}"))
            await pilot.pause()
            assert v.is_vertical_scroll_end, f"Failed to stay at bottom after line {i}"
