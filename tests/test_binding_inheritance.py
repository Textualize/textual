import pytest

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.binding import Binding

##############################################################################
# These are the movement keys within Textual; they kind of have a special
# status in that they will get bound to movement-related methods.
MOVEMENT_KEYS = ["up", "down", "left", "right", "home", "end", "pageup", "pagedown"]

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
class AppWithMovementKeysBound(AppKeyRecorder):
    BINDINGS = [
        Binding("x", "record('x')", "x"),
        *[Binding(key, f"record({key}')", key) for key in MOVEMENT_KEYS],
    ]


async def test_pressing_alpha_on_app() -> None:
    """Test that pressing the an alpha key, when it's bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press(*"xxxxx")
        assert "".join(pilot.app.pressed_keys) == "xxxxx"


@pytest.mark.xfail(
    reason="Up key isn't firing bound action on an app due to key inheritence of its screen [issue#1343]"
)
async def test_pressing_movement_keys_app() -> None:
    """Test that pressing the movement keys, when they're bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press("x", *MOVEMENT_KEYS, "x")
        assert pilot.app.pressed_keys == ["x", *MOVEMENT_KEYS, "x"]


##############################################################################
class WidgetWithBindings(Static, can_focus=True):
    """A widget that has its own bindings for the movement keys."""

    BINDINGS = [
        Binding("x", "record('x')", "x"),
        *[Binding(key, f"local_record('{key}')", key) for key in MOVEMENT_KEYS]
    ]

    async def action_local_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"locally_{key}")


class AppWithWidgetWithBindings(AppKeyRecorder):
    """A test app that composes with a widget that has movement bindings."""

    def compose(self) -> ComposeResult:
        yield WidgetWithBindings()

    def on_mount(self) -> None:
        self.query_one(WidgetWithBindings).focus()


async def test_focused_child_widget_with_movement_bindings() -> None:
    """A focused child widget with movement bindings should handle its own actions."""
    async with AppWithWidgetWithBindings().run_test() as pilot:
        await pilot.press("x", *MOVEMENT_KEYS, "x")
        assert pilot.app.pressed_keys == ["x", *[f"locally_{key}" for key in MOVEMENT_KEYS], "x"]

##############################################################################
class FocusableWidgetWithNoBindings(Static, can_focus=True):
    """A widget that can receive focus but has no bindings."""

class ScreenWithMovementBindings(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = [
        Binding("x", "record('x')", "x"),
        *[Binding(key, f"screen_record('{key}')", key) for key in MOVEMENT_KEYS]
    ]

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screen_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithNoBindings()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithNoBindings).focus()

class AppWithScreenWithBindingsWidgetNoBindings(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings."""

    SCREENS = {"main":ScreenWithMovementBindings}

    def on_mount(self) -> None:
        self.push_screen("main")

@pytest.mark.xfail(
    reason="Movement keys never make it to the screen with such bindings due to key inheritance and pre-bound movement keys [issue#1343]"
)
async def test_focused_child_widget_with_movement_bindings_on_screen() -> None:
    """A focused child widget, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetNoBindings().run_test() as pilot:
        await pilot.press("x", *MOVEMENT_KEYS, "x")
        assert pilot.app.pressed_keys == ["x", *[f"screen_{key}" for key in MOVEMENT_KEYS], "x"]
