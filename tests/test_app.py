import contextlib

from rich.terminal_theme import DIMMED_MONOKAI, MONOKAI, NIGHT_OWLISH

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
        assert button.pseudo_classes == {
            "blur",
            "can-focus",
            "dark",
            "enabled",
        }

        # Take note of the initial background colour
        initial_background = button.styles.background
        await pilot.hover(Button)

        # We've hovered, so ensure the pseudoclass is present and background changed
        assert button.pseudo_classes == {
            "blur",
            "can-focus",
            "dark",
            "enabled",
            "hover",
        }
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


async def test_default_return_code_is_zero():
    app = App()
    async with app.run_test():
        app.exit()
    assert app.return_code == 0


async def test_return_code_is_one_after_crash():
    class MyApp(App):
        def key_p(self):
            1 / 0

    app = MyApp()
    with contextlib.suppress(ZeroDivisionError):
        async with app.run_test() as pilot:
            await pilot.press("p")
    assert app.return_code == 1


async def test_set_return_code():
    app = App()
    async with app.run_test():
        app.exit(return_code=42)
    assert app.return_code == 42


def test_no_return_code_before_running():
    app = App()
    assert app.return_code is None


async def test_no_return_code_while_running():
    app = App()
    async with app.run_test():
        assert app.return_code is None


async def test_ansi_theme():
    app = App()
    async with app.run_test():
        app.ansi_theme_dark = NIGHT_OWLISH
        assert app.ansi_theme == NIGHT_OWLISH

        app.dark = False
        assert app.ansi_theme != NIGHT_OWLISH

        app.ansi_theme_light = MONOKAI
        assert app.ansi_theme == MONOKAI

        # Ensure if we change the dark theme while on light mode,
        # then change back to dark mode, the dark theme is updated.
        app.ansi_theme_dark = DIMMED_MONOKAI
        assert app.ansi_theme == MONOKAI

        app.dark = True
        assert app.ansi_theme == DIMMED_MONOKAI
