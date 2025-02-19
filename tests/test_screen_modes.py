from itertools import cycle
from typing import Type

import pytest

from textual.app import (
    ActiveModeError,
    App,
    ComposeResult,
    InvalidModeError,
    UnknownModeError,
)
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Label


class ScreenBindingsMixin(Screen[None]):
    BINDINGS = [
        ("1", "one", "Mode 1"),
        ("2", "two", "Mode 2"),
        ("p", "push", "Push rnd scrn"),
        ("o", "app.pop_screen", "Pop"),
        ("r", "remove", "Remove mode 1"),
    ]

    def action_one(self) -> None:
        self.app.switch_mode("one")

    def action_two(self) -> None:
        self.app.switch_mode("two")

    def action_fruits(self) -> None:
        self.app.switch_mode("fruits")

    def action_push(self) -> None:
        self.app.push_screen(FruitModal())


class BaseScreen(ScreenBindingsMixin):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.label)
        yield Footer()

    def action_remove(self) -> None:
        self.app.remove_mode("one")


class FruitModal(ModalScreen[str], ScreenBindingsMixin):
    BINDINGS = [("d", "dismiss_fruit", "Dismiss")]

    def compose(self) -> ComposeResult:
        FRUITS = cycle(
            "apple mango strawberry banana peach pear melon watermelon".split()
        )
        yield Label(next(FRUITS))


@pytest.fixture
def ModesApp():
    class ModesApp(App[None]):
        MODES = {
            "one": lambda: BaseScreen("one"),
            "two": "screen_two",
        }

        SCREENS = {
            "screen_two": lambda: BaseScreen("two"),
        }

        def on_mount(self):
            self.switch_mode("one")

    return ModesApp


async def test_mode_setup(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test():
        assert isinstance(app.screen, BaseScreen)
        assert str(app.screen.query_one(Label).renderable) == "one"


async def test_switch_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test() as pilot:
        await pilot.press("2")
        assert str(app.screen.query_one(Label).renderable) == "two"
        await pilot.press("1")
        assert str(app.screen.query_one(Label).renderable) == "one"


async def test_switch_same_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test() as pilot:
        await pilot.press("1")
        assert str(app.screen.query_one(Label).renderable) == "one"
        await pilot.press("1")
        assert str(app.screen.query_one(Label).renderable) == "one"


async def test_switch_unknown_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test():
        with pytest.raises(UnknownModeError):
            await app.switch_mode("unknown mode here")


async def test_remove_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test() as pilot:
        await app.switch_mode("two")
        await pilot.pause()
        assert str(app.screen.query_one(Label).renderable) == "two"
        app.remove_mode("one")
        assert "one" not in app._modes


async def test_remove_active_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test():
        with pytest.raises(ActiveModeError):
            app.remove_mode("one")


async def test_add_mode(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test() as pilot:
        app.add_mode("three", lambda: BaseScreen("three"))
        await app.switch_mode("three")
        await pilot.pause()
        assert str(app.screen.query_one(Label).renderable) == "three"


async def test_add_mode_duplicated(ModesApp: Type[App]):
    app = ModesApp()
    async with app.run_test():
        with pytest.raises(InvalidModeError):
            app.add_mode("one", lambda: BaseScreen("one"))


async def test_screen_stack_preserved(ModesApp: Type[App]):
    fruits = []
    N = 5

    app = ModesApp()
    async with app.run_test() as pilot:
        # Build the stack up.
        for _ in range(N):
            await pilot.press("p")
            fruits.append(str(app.screen.query_one(Label).renderable))

        assert len(app.screen_stack) == N + 1

        # Switch out and back.
        await pilot.press("2")
        assert len(app.screen_stack) == 1
        await pilot.press("1")

        # Check the stack.
        assert len(app.screen_stack) == N + 1
        for _ in range(N):
            assert str(app.screen.query_one(Label).renderable) == fruits.pop()
            await pilot.press("o")


async def test_multiple_mode_callbacks():
    written = []

    class LogScreen(Screen[None]):
        def __init__(self, value):
            super().__init__()
            self.value = value

        def key_p(self) -> None:
            self.app.push_screen(ResultScreen(self.value), written.append)

    class ResultScreen(Screen[str]):
        def __init__(self, value):
            super().__init__()
            self.value = value

        def key_p(self) -> None:
            self.dismiss(self.value)

        def key_f(self) -> None:
            self.app.switch_mode("first")

        def key_o(self) -> None:
            self.app.switch_mode("other")

    class ModesApp(App[None]):
        MODES = {
            "first": lambda: LogScreen("first"),
            "other": lambda: LogScreen("other"),
        }

        def on_mount(self) -> None:
            self.switch_mode("first")

        def key_f(self) -> None:
            self.switch_mode("first")

        def key_o(self) -> None:
            self.switch_mode("other")

    app = ModesApp()
    async with app.run_test() as pilot:
        # Push and dismiss ResultScreen("first")
        await pilot.press("p")
        await pilot.press("p")
        assert written == ["first"]

        # Push ResultScreen("first")
        await pilot.press("p")
        # Switch to LogScreen("other")
        await pilot.press("o")
        # Push and dismiss ResultScreen("other")
        await pilot.press("p")
        await pilot.press("p")
        assert written == ["first", "other"]

        # Go back to ResultScreen("first")
        await pilot.press("f")
        # Dismiss ResultScreen("first")
        await pilot.press("p")
        assert written == ["first", "other", "first"]
