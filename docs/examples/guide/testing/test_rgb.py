from rgb import RGBApp

from textual.color import Color


async def test_keys():  # (1)!
    """Test pressing keys has the desired result."""
    app = RGBApp()
    async with app.run_test() as pilot:  # (2)!
        # Test pressing the R key
        await pilot.press("r")  # (3)!
        assert app.screen.styles.background == Color.parse("red")  # (4)!

        # Test pressing the G key
        await pilot.press("g")
        assert app.screen.styles.background == Color.parse("green")

        # Test pressing the B key
        await pilot.press("b")
        assert app.screen.styles.background == Color.parse("blue")

        # Test pressing the X key
        await pilot.press("x")
        # No binding (so no change to the color)
        assert app.screen.styles.background == Color.parse("blue")


async def test_buttons():
    """Test pressing keys has the desired result."""
    app = RGBApp()
    async with app.run_test() as pilot:
        # Test clicking the "red" button
        await pilot.click("#red")  # (5)!
        assert app.screen.styles.background == Color.parse("red")

        # Test clicking the "green" button
        await pilot.click("#green")
        assert app.screen.styles.background == Color.parse("green")

        # Test clicking the "blue" button
        await pilot.click("#blue")
        assert app.screen.styles.background == Color.parse("blue")
