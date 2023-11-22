"""Regression test for https://github.com/Textualize/textual/issues/2914

Make sure that calls to render only happen after a widget being mounted.
"""

import asyncio

from textual.app import App
from textual.widget import Widget


class W(Widget):
    def render(self):
        return self.renderable

    async def on_mount(self):
        await asyncio.sleep(0.1)
        self.renderable = "1234"


async def test_render_only_after_mount():
    """Regression test for https://github.com/Textualize/textual/issues/2914"""
    app = App()
    async with app.run_test() as pilot:
        app.mount(W())
        app.mount(W())
        await pilot.pause()
