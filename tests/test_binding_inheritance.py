import pytest

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.binding import Binding

##############################################################################
class NoBindings(App[None]):
    """An app with zero bindings."""


async def test_just_app_no_bindings() -> None:
    """An app with no bindings should have no bindings, other than ctrl+c."""
    async with NoBindings().run_test() as pilot:
        assert list(pilot.app._bindings.keys.keys()) == ["ctrl+c"]


##############################################################################
class AlphaBinding(App[None]):
    """An app with a simple alpha key binding."""

    BINDINGS = [Binding("a", "a", "a")]


async def test_just_app_alpha_binding() -> None:
    """An app with a single binding should have just the one binding."""
    async with AlphaBinding().run_test() as pilot:
        assert sorted(pilot.app._bindings.keys.keys()) == sorted(["ctrl+c", "a"])


##############################################################################
class ScreenNoBindings(Screen):
    """A screen with no added bindings."""


class AppWithScreenNoBindings(App[None]):
    """An app with no extra bindings but with a custom screen."""

    SCREENS = {"main": ScreenNoBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


@pytest.mark.xfail(
    reason="Screen is incorrectly starting with bindings for movement keys [issue#1343]"
)
async def test_app_screen_no_bindings() -> None:
    """An screen with no bindings should have no bindings."""
    async with AppWithScreenNoBindings().run_test() as pilot:
        assert list(pilot.app.screen._bindings.keys.keys()) == []


##############################################################################
class ScreenWithBindings(Screen):
    """A screen with a simple alpha key binding."""

    BINDINGS = [Binding("a", "a", "a")]


class AppWithScreenThatHasABinding(App[None]):
    """An app with no extra bindings but with a custom screen with a binding."""

    SCREENS = {"main": ScreenWithBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


@pytest.mark.xfail(
    reason="Screen is incorrectly starting with bindings for movement keys [issue#1343]"
)
async def test_app_screen_with_bindings() -> None:
    """An app with a screen and a binding should only have ctrl+c as a binding."""
    async with AppWithScreenThatHasABinding().run_test() as pilot:
        assert list(pilot.app.screen._bindings.keys.keys()) == ["a"]

##############################################################################
class NoBindingsAndStaticWidgetNoBindings(App[None]):
    """An app with no bindings, enclosing a widget with no bindings."""

    def compose(self) -> ComposeResult:
        yield Static("Poetry! They should have sent a poet.")

@pytest.mark.xfail(
    reason="Static is incorrectly starting with bindings for movement keys [issue#1343]"
)
async def test_just_app_no_bindings_widget_no_bindings() -> None:
    """A widget with no bindings should have no bindings. Its app should have just ctrl+c"""
    async with NoBindingsAndStaticWidgetNoBindings().run_test() as pilot:
        assert list(pilot.app._bindings.keys.keys()) == ["ctrl+c"]
        assert list(pilot.app.screen.query_one(Static)._bindings.keys.keys()) == []

##############################################################################
class AppKeyRecorder(App[None]):

    def __init__(self) -> None:
        super().__init__()
        self.pressed_keys: list[str] = []

    async def action_record(self, key: str) -> None:
        self.pressed_keys.append(key)

##############################################################################
class AppWithUpKeyBound(AppKeyRecorder):
    BINDINGS=[
        Binding("x","record('x')","x"),
        Binding("up","record('up')","up")
    ]

async def test_pressing_alpha_on_app() -> None:
    """Test that pressing the an alpha key, when it's bound on the app, results in an action fire."""
    async with AppWithUpKeyBound().run_test() as pilot:
        await pilot.press(*"xxxxx")
        assert "".join(pilot.app.pressed_keys) == "xxxxx"

@pytest.mark.xfail(
    reason="Up key isn't firing bound action on an app due to key inheritence of its screen [issue#1343]"
)
async def test_pressing_up_on_app() -> None:
    """Test that pressing the up key, when it's bound on the app, results in an action fire."""
    async with AppWithUpKeyBound().run_test() as pilot:
        await pilot.press("x", "up", "x")
        assert pilot.app.pressed_keys == ["x", "up", "x"]

