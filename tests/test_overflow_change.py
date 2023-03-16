"""Regression test for #1616 https://github.com/Textualize/textual/issues/1616"""

from textual.app import App
from textual.containers import VerticalScroll


async def test_overflow_change_updates_virtual_size_appropriately():
    class MyApp(App):
        def compose(self):
            yield VerticalScroll()

    app = MyApp()

    async with app.run_test() as pilot:
        vertical = app.query_one(VerticalScroll)

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
