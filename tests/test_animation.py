import asyncio
from time import time

from textual.app import App, ComposeResult
from textual.widgets import Static


class AnimApp(App):
    CSS = """
    #foo {
        height: 1;
    }
    
    """

    def compose(self) -> ComposeResult:
        yield Static("foo", id="foo")


async def test_animate_height() -> None:
    """Test animating styles.height works."""

    # Styles.height is a scalar, which makes it more complicated to animate

    app = AnimApp()

    async with app.run_test() as pilot:
        static = app.query_one(Static)
        assert static.size.height == 1
        static.styles.animate("height", 100, duration=0.5, easing="linear")
        start = time()

        # Wait for half the animation
        await pilot.pause(0.25)
        # Check we reached the half way point
        assert static.styles.height.value >= 50
        elapsed = time() - start
        # Check at least that much time has elapsed
        assert 0.5 > elapsed > 0.25
        # Wait for the animation to finished
        await pilot.wait_for_animation()
        elapsed = time() - start
        # Check that the full time has elapsed
        assert elapsed > 0.5
        # Check the height reached the maximum
        assert static.styles.height.value == 100
