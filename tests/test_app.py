from textual.app import App, ComposeResult
from textual.widgets import Button, Input


def test_batch_update():
    """Test `batch_update` context manager"""
    app = App()
    assert app._batch_count == 0  # Start at zero

    with app.batch_update():
        assert app._batch_count == 1  # Increments in context manager

        with app.batch_update():
            assert app._batch_count == 2  # Nested updates

        assert app._batch_count == 1  # Exiting decrements

    assert app._batch_count == 0  # Back to zero


class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Input()
        yield Button("Click me!")


async def test_hover_update_styles():
    app = MyApp()
    async with app.run_test() as pilot:
        button = app.query_one(Button)
        assert button.pseudo_classes == {"enabled", "can-focus"}

        # Take note of the initial background colour
        initial_background = button.styles.background
        await pilot.hover(Button)

        # We've hovered, so ensure the pseudoclass is present and background changed
        assert button.pseudo_classes == {"enabled", "hover", "can-focus"}
        assert button.styles.background != initial_background


def test_setting_title():
    app = MyApp()
    app.title = None
    assert app.title == "None"

    app.title = ""
    assert app.title == ""

    app.title = 0.125
    assert app.title == "0.125"

    app.title = [True, False, 2]
    assert app.title == "[True, False, 2]"


def test_setting_sub_title():
    app = MyApp()
    app.sub_title = None
    assert app.sub_title == "None"

    app.sub_title = ""
    assert app.sub_title == ""

    app.sub_title = 0.125
    assert app.sub_title == "0.125"

    app.sub_title = [True, False, 2]
    assert app.sub_title == "[True, False, 2]"
