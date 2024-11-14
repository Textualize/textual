import contextlib

from rich.terminal_theme import DIMMED_MONOKAI, MONOKAI, NIGHT_OWLISH

from textual.app import App, ComposeResult
from textual.command import SimpleCommand
from textual.widgets import Button, Input, Static


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
    app = MyApp(ansi_color=False)
    async with app.run_test() as pilot:
        button = app.query_one(Button)
        assert button.pseudo_classes == {
            "blur",
            "can-focus",
            "dark",
            "enabled",
            "first-of-type",
            "last-of-type",
            "even",
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
            "first-of-type",
            "last-of-type",
            "even",
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

        app.theme = "textual-light"
        assert app.ansi_theme != NIGHT_OWLISH

        app.ansi_theme_light = MONOKAI
        assert app.ansi_theme == MONOKAI

        # Ensure if we change the dark theme while on light mode,
        # then change back to dark mode, the dark theme is updated.
        app.ansi_theme_dark = DIMMED_MONOKAI
        assert app.ansi_theme == MONOKAI

        app.theme = "textual-dark"
        assert app.ansi_theme == DIMMED_MONOKAI


async def test_early_exit():
    """Test exiting early doesn't cause issues."""
    from textual.app import App

    class AppExit(App):
        def compose(self):
            yield Static("Hello")

        def on_mount(self) -> None:
            # Exit after creating app
            self.exit()

    app = AppExit()
    async with app.run_test():
        pass


def test_early_exit_inline():
    """Test exiting early in inline mode doesn't break."""

    class AppExit(App[None]):
        def compose(self):
            yield Static("Hello")

        def on_mount(self) -> None:
            # Exit after creating app
            self.exit()

    app = AppExit()
    app.run(inline=True, inline_no_clear=True)


async def test_search_with_simple_commands():
    """Test search with a list of SimpleCommands and ensure callbacks are invoked."""
    called = False

    def callback():
        nonlocal called
        called = True

    app = App[None]()
    commands = [
        SimpleCommand("Test Command", callback, "A test command"),
        SimpleCommand("Another Command", callback, "Another test command"),
    ]
    async with app.run_test() as pilot:
        await app.search_commands(commands)
        await pilot.press("enter", "enter")
        assert called


async def test_search_with_tuples():
    """Test search with a list of tuples and ensure callbacks are invoked.
    In this case we also have no help text in the tuples.
    """
    called = False

    def callback():
        nonlocal called
        called = True

    app = App[None]()
    commands = [
        ("Test Command", callback),
        ("Another Command", callback),
    ]
    async with app.run_test() as pilot:
        await app.search_commands(commands)
        await pilot.press("enter", "enter")
        assert called


async def test_search_with_empty_list():
    """Test search with an empty command list doesn't crash."""
    app = App[None]()
    async with app.run_test() as pilot:
        await app.search_commands([])
        await pilot.press("escape")
