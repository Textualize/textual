"""Regression test for #1616 https://github.com/Textualize/textual/issues/1616"""
import pytest

from textual.app import App
from textual.containers import Vertical


async def test_overflow_change_updates_virtual_size_appropriately():
    class MyApp(App):
        def compose(self):
            yield Vertical()

    app = MyApp()

    async with app.run_test() as pilot:
        vertical = app.query_one(Vertical)

        height = vertical.virtual_size.height

        vertical.styles.overflow_x = "scroll"
        await pilot.pause()  # Let changes propagate.
        assert vertical.virtual_size.height < height

        vertical.styles.overflow_x = "hidden"
        await pilot.pause()
        assert vertical.virtual_size.height == height

        width = vertical.virtual_size.width

        vertical.styles.overflow_y = "scroll"
        await pilot.pause()
        assert vertical.virtual_size.width < width

        vertical.styles.overflow_y = "hidden"
        await pilot.pause()
        assert vertical.virtual_size.width == width
