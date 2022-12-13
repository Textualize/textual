"""Tests relating to key binding inheritance.

In here you'll find some tests for general key binding inheritance, but
there is an emphasis on the inheriting of movement key bindings as they (as
of the time of writing) hold a special place in the Widget hierarchy of
Textual.

<URL:https://github.com/Textualize/textual/issues/1343> holds much of the
background relating to this.
"""

from __future__ import annotations

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
# An application with no bindings anywhere.
#
# The idea of this first little test is that an application that has no
# bindings set anywhere, and uses a default screen, should only have the one
# binding in place: ctrl+c; it's hard-coded in the app class for now.

class NoBindings(App[None]):
    """An app with zero bindings."""


async def test_just_app_no_bindings() -> None:
    """An app with no bindings should have no bindings, other than ctrl+c."""
    async with NoBindings().run_test() as pilot:
        assert list(pilot.app._bindings.keys.keys()) == ["ctrl+c"]


##############################################################################
# An application with a single alpha binding.
#
# Sticking with just an app and the default screen: this configuration has a
# BINDINGS on the app itself, and simply binds the letter a -- in other
# words avoiding anything to do with movement keys. The result should be
# that we see the letter a, ctrl+c, and nothing else.

class AlphaBinding(App[None]):
    """An app with a simple alpha key binding."""

    BINDINGS = [Binding("a", "a", "a")]


async def test_just_app_alpha_binding() -> None:
    """An app with a single binding should have just the one binding."""
    async with AlphaBinding().run_test() as pilot:
        assert sorted(pilot.app._bindings.keys.keys()) == sorted(["ctrl+c", "a"])


##############################################################################
# Introduce a non-default screen.
#
# Having tested an app using the default screen, we now introduce a
# non-default screen. Generally this won't make a difference, but we *are*
# working with a subsclass of Screen now so this should be covered.
#
# To start with the screen has no bindings -- it's just a direct subclass
# with no other changes.

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
async def test_app_screen_has_no_movement_bindings() -> None:
    """A screen with no bindings should not have movement key bindings."""
    async with AppWithScreenNoBindings().run_test() as pilot:
        assert sorted(list(pilot.app.screen._bindings.keys.keys())) != sorted(MOVEMENT_KEYS)


##############################################################################
# Add an alpha-binding to a non-default screen.
#
# Hacking checked things with a non-default screen with no bindings, let's
# now do the same thing but with a binding added that isn't for a movement
# key.

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
    """A screen with a single alpha key binding should only have that key as a binding."""
    async with AppWithScreenThatHasABinding().run_test() as pilot:
        assert list(pilot.app.screen._bindings.keys.keys()) == ["a"]


##############################################################################
# An app with a non-default screen wrapping a Static.
#
# So far the screens we've been pushing likely haven't passed the test of
# being a container. So now we test with zero bindings in place, expecting
# to see zero bindings in place, but do so when the screen has a child;
# presumably making it pass as a container.

class NoBindingsAndStaticWidgetNoBindings(App[None]):
    """An app with no bindings, enclosing a widget with no bindings."""

    def compose(self) -> ComposeResult:
        yield Static("Poetry! They should have sent a poet.")


@pytest.mark.xfail(
    reason="Static is incorrectly starting with bindings for movement keys [issue#1343]"
)
async def test_just_app_no_bindings_widget_no_bindings() -> None:
    """A widget with no bindings should have no bindings"""
    async with NoBindingsAndStaticWidgetNoBindings().run_test() as pilot:
        assert list(pilot.app.screen.query_one(Static)._bindings.keys.keys()) == []


##############################################################################
# From here on in we're going to start simulating key strokes to ensure that
# any bindings that are in place actually fire the correct actions. To help
# with this let's build a simple key/binding/action recorder base app.

class AppKeyRecorder(App[None]):
    """Base application class that can be used to record keystrokes."""

    ALPHAS = "abcxyz"
    """str: The alpha keys to test against."""

    ALL_KEYS = [*ALPHAS, *MOVEMENT_KEYS]
    """list[str]: All the test keys."""

    @staticmethod
    def mk_bindings(prefix: str="") -> list[Binding]:
        """Make the binding list for testing an app.

        Args:
            prefix (str, optional): An optional prefix for the actions.

        Returns:
            list[Binding]: The resulting list of bindings.
        """
        return [
            Binding( key, f"{prefix}record('{key}')", key ) for key in [*AppKeyRecorder.ALPHAS, *MOVEMENT_KEYS]
        ]

    def __init__(self) -> None:
        """Initialise the recording app."""
        super().__init__()
        self.pressed_keys: list[str] = []

    async def action_record(self, key: str) -> None:
        """Record a key, as used from a binding.

        Args:
            key (str): The name of the key to record.
        """
        self.pressed_keys.append(key)


##############################################################################
# An app with bindings for movement keys.
#
# Having gone through various permutations of testing for what bindings are
# seen to be in place, we now move on to adding bindings, invoking them and
# seeing what happens. First off let's start with an application that has
# bindings, both for an alpha key, and also for all of the movement keys.

class AppWithMovementKeysBound(AppKeyRecorder):
    """An application with bindings."""
    BINDINGS = AppKeyRecorder.mk_bindings()


async def test_pressing_alpha_on_app() -> None:
    """Test that pressing the alpha key, when it's bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALPHAS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [*AppKeyRecorder.ALPHAS]


@pytest.mark.xfail(
    reason="Up key isn't firing bound action on an app due to key inheritence of its screen [issue#1343]"
)
async def test_pressing_movement_keys_app() -> None:
    """Test that pressing the movement keys, when they're bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == AppKeyRecorder.ALL_KEYS


##############################################################################
# An app with a focused child widget with bindings.
#
# Now let's spin up an application, using the default screen, where the app
# itself is composing in a widget that can have, and has, focus. The widget
# also has bindings for all of the test keys. That child widget should be
# able to handle all of the test keys on its own and nothing else should
# grab them.

class FocusableWidgetWithBindings(Static, can_focus=True):
    """A widget that has its own bindings for the movement keys."""
    BINDINGS = AppKeyRecorder.mk_bindings("local_")

    async def action_local_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"locally_{key}")


class AppWithWidgetWithBindings(AppKeyRecorder):
    """A test app that composes with a widget that has movement bindings."""

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithBindings()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithBindings).focus()


async def test_focused_child_widget_with_movement_bindings() -> None:
    """A focused child widget with movement bindings should handle its own actions."""
    async with AppWithWidgetWithBindings().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [f"locally_{key}" for key in AppKeyRecorder.ALL_KEYS]

##############################################################################
# A focused widget within a screen that handles bindings.
#
# Similar to the previous test, here we're wrapping an app around a
# non-default screen, which in turn wraps a widget that can has, and will
# have, focus. The difference here however is that the screen has the
# bindings. What we should expect to see is that the bindings don't fire on
# the widget (it has none) and instead get caught by the screen.

class FocusableWidgetWithNoBindings(Static, can_focus=True):
    """A widget that can receive focus but has no bindings."""

class ScreenWithMovementBindings(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.mk_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

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
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [f"screenly_{key}" for key in AppKeyRecorder.ALL_KEYS]

##############################################################################
# A focused widget with bindings but no inheriting of bindings, on app.
#
# Now we move on to testing inherit_bindings. To start with we go back to an
# app with a default screen, with the app itself composing in a widget that
# can and will have focus, which has bindings for all the test keys, and
# crucially has inherit_bindings set to False.
#
# We should expect to see all of the test keys recorded post-press.

class WidgetWithBindingsNoInherit(Static, can_focus=True, inherit_bindings=False):
    """A widget that has its own bindings for the movement keys, no binding inheritance."""
    BINDINGS = AppKeyRecorder.mk_bindings("local_")

    async def action_local_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"locally_{key}")


class AppWithWidgetWithBindingsNoInherit(AppKeyRecorder):
    """A test app that composes with a widget that has movement bindings without binding inheritance."""

    def compose(self) -> ComposeResult:
        yield WidgetWithBindingsNoInherit()

    def on_mount(self) -> None:
        self.query_one(WidgetWithBindingsNoInherit).focus()


async def test_focused_child_widget_with_movement_bindings_no_inherit() -> None:
    """A focused child widget with movement bindings and inherit_bindings=False should handle its own actions."""
    async with AppWithWidgetWithBindingsNoInherit().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [f"locally_{key}" for key in AppKeyRecorder.ALL_KEYS]

##############################################################################
# A focused widget with no bindings and no inheriting of bindings, on screen.
#
# Now let's test with a widget that can and will have focus, which has no
# bindings, and which won't inherit bindings either. The bindings we're
# going to test are moved up to the screen. We should expect to see all of
# the test keys not be consumed by the focused widget, but instead they
# should make it up to the screen.
#
# NOTE: no bindings are declared for the widget, which is different from
# zero bindings declared.

class FocusableWidgetWithNoBindingsNoInherit(Static, can_focus=True, inherit_bindings=False):
    """A widget that can receive focus but has no bindings and doesn't inherit bindings."""

class ScreenWithMovementBindingsNoInheritChild(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.mk_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithNoBindingsNoInherit()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithNoBindingsNoInherit).focus()

class AppWithScreenWithBindingsWidgetNoBindingsNoInherit(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings, child no-inherit."""

    SCREENS = {"main":ScreenWithMovementBindingsNoInheritChild}

    def on_mount(self) -> None:
        self.push_screen("main")

async def test_focused_child_widget_no_inherit_with_movement_bindings_on_screen() -> None:
    """A focused child widget, that doesn't inherit bindings, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetNoBindingsNoInherit().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [f"screenly_{key}" for key in AppKeyRecorder.ALL_KEYS]

##############################################################################
# A focused widget with zero bindings declared, but no inheriting of
# bindings, on screen.
#
# Now let's test with a widget that can and will have focus, which has zero
# (an empty collection of) bindings, and which won't inherit bindings
# either. The bindings we're going to test are moved up to the screen. We
# should expect to see all of the test keys not be consumed by the focused
# widget, but instead they should make it up to the screen.
#
# NOTE: zero bindings are declared for the widget, which is different from
# no bindings declared.

class FocusableWidgetWithEmptyBindingsNoInherit(Static, can_focus=True, inherit_bindings=False):
    """A widget that can receive focus but has empty bindings and doesn't inherit bindings."""
    BINDINGS = []

class ScreenWithMovementBindingsNoInheritEmptyChild(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.mk_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithEmptyBindingsNoInherit()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithEmptyBindingsNoInherit).focus()

class AppWithScreenWithBindingsWidgetEmptyBindingsNoInherit(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings, child no-inherit."""

    SCREENS = {"main":ScreenWithMovementBindingsNoInheritEmptyChild}

    def on_mount(self) -> None:
        self.push_screen("main")

async def test_focused_child_widget_no_inherit_empty_bindings_with_movement_bindings_on_screen() -> None:
    """A focused child widget, that doesn't inherit bindings and sets BINDINGS empty, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetEmptyBindingsNoInherit().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause(2/100)
        assert pilot.app.pressed_keys == [f"screenly_{key}" for key in AppKeyRecorder.ALL_KEYS]
