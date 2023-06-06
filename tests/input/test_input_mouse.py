from __future__ import annotations

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Input


class InputApp(App[None]):
    TEST_TEXT = "That gum you like is going to come back in style"

    def compose(self) -> ComposeResult:
        yield Input(self.TEST_TEXT)


async def test_mouse_clicks_within():
    """Mouse clicks should result in the cursor going to the right place."""
    async with InputApp().run_test() as pilot:
        for click_at, should_land in (
            (0, 0),
            (1, 1),
            (10, 10),
            (len(InputApp.TEST_TEXT) - 1, len(InputApp.TEST_TEXT) - 1),
            (len(InputApp.TEST_TEXT), len(InputApp.TEST_TEXT)),
            (len(InputApp.TEST_TEXT) * 2, len(InputApp.TEST_TEXT)),
        ):
            # Note the offsets to take into account the decoration around an
            # Input.
            await pilot.click(Input, Offset(click_at + 3, 1))
            await pilot.pause()
            assert pilot.app.query_one(Input).cursor_position == should_land


async def test_mouse_click_outwith():
    """Mouse clicks outside the input should not affect cursor position."""
    async with InputApp().run_test() as pilot:
        pilot.app.query_one(Input).cursor_position = 3
        assert pilot.app.query_one(Input).cursor_position == 3
        await pilot.click(Input, Offset(0, 0))
        await pilot.pause()
        assert pilot.app.query_one(Input).cursor_position == 3
