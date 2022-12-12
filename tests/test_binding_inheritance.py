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
