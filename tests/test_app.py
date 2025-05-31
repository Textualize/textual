import asyncio
import contextlib

import pytest
from rich.terminal_theme import DIMMED_MONOKAI, MONOKAI, NIGHT_OWLISH

from textual import events
from textual.app import App, ComposeResult
from textual.command import SimpleCommand
from textual.pilot import Pilot, _get_mouse_message_arguments
from textual.widgets import Button, Input, Label, Static


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
            "last-child",
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
            "last-child",
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
    async with app.run_test():
        await app.search_commands([])


async def raw_click(pilot: Pilot, selector: str, times: int = 1):
    """A lower level click function that doesn't use the Pilot,
    and so doesn't bypass the click chain logic in App.on_event."""
    app = pilot.app
    kwargs = _get_mouse_message_arguments(app.query_one(selector))
    for _ in range(times):
        app.post_message(events.MouseDown(**kwargs))
        app.post_message(events.MouseUp(**kwargs))
        await pilot.pause()


@pytest.mark.parametrize("number_of_clicks,final_count", [(1, 1), (2, 3), (3, 6)])
async def test_click_chain_initial_repeated_clicks(
    number_of_clicks: int, final_count: int
):
    click_count = 0

    class MyApp(App[None]):
        # Ensure clicks are always within the time threshold
        CLICK_CHAIN_TIME_THRESHOLD = 1000.0

        def compose(self) -> ComposeResult:
            yield Label("Click me!", id="one")

        def on_click(self, event: events.Click) -> None:
            nonlocal click_count
            print(f"event: {event}")
            click_count += event.chain

    async with MyApp().run_test() as pilot:
        # Clicking the same Label at the same offset creates a double and triple click.
        for _ in range(number_of_clicks):
            await raw_click(pilot, "#one")

        assert click_count == final_count


async def test_click_chain_different_offset():
    click_count = 0

    class MyApp(App[None]):
        # Ensure clicks are always within the time threshold
        CLICK_CHAIN_TIME_THRESHOLD = 1000.0

        def compose(self) -> ComposeResult:
            yield Label("One!", id="one")
            yield Label("Two!", id="two")
            yield Label("Three!", id="three")

        def on_click(self, event: events.Click) -> None:
            nonlocal click_count
            click_count += event.chain

    async with MyApp().run_test() as pilot:
        # Clicking on different offsets in quick-succession doesn't qualify as a double or triple click.
        await raw_click(pilot, "#one")
        assert click_count == 1
        await raw_click(pilot, "#two")
        assert click_count == 2
        await raw_click(pilot, "#three")
        assert click_count == 3


async def test_click_chain_offset_changes_mid_chain():
    """If we're in the middle of a click chain (e.g. we've double clicked), and the third click
    comes in at a different offset, that third click should be considered a single click.
    """

    click_count = 0

    class MyApp(App[None]):
        # Ensure clicks are always within the time threshold
        CLICK_CHAIN_TIME_THRESHOLD = 1000.0

        def compose(self) -> ComposeResult:
            yield Label("Click me!", id="one")
            yield Label("Another button!", id="two")

        def on_click(self, event: events.Click) -> None:
            nonlocal click_count
            click_count = event.chain

    async with MyApp().run_test() as pilot:
        await raw_click(pilot, "#one", times=2)  # Double click
        assert click_count == 2
        await raw_click(pilot, "#two")  # Single click (because different widget)
        assert click_count == 1


async def test_click_chain_time_outwith_threshold():
    click_count = 0

    class MyApp(App[None]):
        # Intentionally set the threshold to 0.0 to ensure we always exceed it
        # and can confirm that a click chain is never created
        CLICK_CHAIN_TIME_THRESHOLD = 0.0

        def compose(self) -> ComposeResult:
            yield Label("Click me!", id="one")

        def on_click(self, event: events.Click) -> None:
            nonlocal click_count
            click_count += event.chain

    async with MyApp().run_test() as pilot:
        for i in range(1, 4):
            # Each click is outwith the time threshold, so a click chain is never created.
            await raw_click(pilot, "#one")
            assert click_count == i


def test_app_loop() -> None:
    """Test that App.run accepts a loop argument."""

    class MyApp(App[int]):
        def on_mount(self) -> None:
            self.exit(42)

    app = MyApp()
    result = app.run(loop=asyncio.new_event_loop())
    assert result == 42


async def test_app_run_async() -> None:
    """Check run_async runs without issues."""

    class MyApp(App[int]):
        def on_mount(self) -> None:
            self.exit(42)

    app = MyApp()
    result = await app.run_async()
    assert result == 42


def test_app_loop_run_after_asyncio_run() -> None:
    """Test that App.run runs after asyncio.run has run."""

    class MyApp(App[int]):
        def on_mount(self) -> None:
            self.exit(42)

    async def amain():
        pass

    asyncio.run(amain())

    app = MyApp()
    result = app.run()
    assert result == 42
