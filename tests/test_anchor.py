from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


async def test_anchor_streaming_repro_flow() -> None:
    class AnchorStuck(App):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="v"):
                for i in range(30):
                    yield Static(f"line {i}")

    app = AnchorStuck()
    async with app.run_test() as pilot:
        v = app.query_one("#v", VerticalScroll)
        v.anchor()
        await pilot.pause()

        assert v.is_anchored
        assert not v._anchor_released
        assert v.scroll_y == v.max_scroll_y

        # User scrolls up by 1 line while streaming
        v.scroll_relative(y=-1, animate=False)
        await pilot.pause()
        assert v._anchor_released is True
        frozen_scroll_y = v.scroll_y

        # Mounting items while released keeps scroll position frozen
        v.mount(Static("new line 0"))
        await pilot.pause()
        assert v._anchor_released is True
        assert v.scroll_y == frozen_scroll_y

        # User scrolls back down to bottom edge
        v.scroll_to(y=v.max_scroll_y, animate=False)
        await pilot.pause()
        assert v._anchor_released is False
        assert v.scroll_y == v.max_scroll_y

        # Mounting new items after re-engaging keeps viewport glued to bottom
        v.mount(Static("new line 1"))
        await pilot.pause()
        assert v._anchor_released is False
        assert v.scroll_y == v.max_scroll_y
