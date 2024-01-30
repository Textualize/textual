"""Tests relating to key binding inheritance.

In here you'll find some tests for general key binding inheritance, but
there is an emphasis on the inheriting of movement key bindings as they (as
of the time of writing) hold a special place in the Widget hierarchy of
Textual.

<URL:https://github.com/Textualize/textual/issues/1343> holds much of the
background relating to this.
"""

from __future__ import annotations

from textual.actions import SkipAction
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Static

##############################################################################
# These are the movement keys within Textual; they kind of have a special
# status in that they will get bound to movement-related methods.
MOVEMENT_KEYS = ["up", "down", "left", "right", "home", "end", "pageup", "pagedown"]

##############################################################################
# An application with no bindings anywhere.
#
# The idea of this first little test is that an application that has no
# bindings set anywhere, and uses a default screen, should only its
# hard-coded bindings in place.


class NoBindings(App[None]):
    """An app with zero bindings."""


async def test_just_app_no_bindings() -> None:
    """An app with no bindings should have no bindings, other than the app's hard-coded ones."""
    async with NoBindings().run_test() as pilot:
        assert list(pilot.app._bindings.keys.keys()) == [
            "ctrl+c",
            "ctrl+backslash",
        ]
        assert pilot.app._bindings.get_key("ctrl+c").priority is True


##############################################################################
# An application with a single alpha binding.
#
# Sticking with just an app and the default screen: this configuration has a
# BINDINGS on the app itself, and simply binds the letter a. The result
# should be that we see the letter a, the app's default bindings, and
# nothing else.


class AlphaBinding(App[None]):
    """An app with a simple alpha key binding."""

    BINDINGS = [Binding("a", "a", "a", priority=True)]


async def test_just_app_alpha_binding() -> None:
    """An app with a single binding should have just the one binding."""
    async with AlphaBinding().run_test() as pilot:
        assert sorted(pilot.app._bindings.keys.keys()) == sorted(
            ["ctrl+c", "ctrl+backslash", "a"]
        )
        assert pilot.app._bindings.get_key("ctrl+c").priority is True
        assert pilot.app._bindings.get_key("a").priority is True


##############################################################################
# An application with a single low-priority alpha binding.
#
# The same as the above, but in this case we're going to, on purpose, lower
# the priority of our own bindings, while any define by App itself should
# remain the same.


class LowAlphaBinding(App[None]):
    """An app with a simple low-priority alpha key binding."""

    BINDINGS = [Binding("a", "a", "a", priority=False)]


async def test_just_app_low_priority_alpha_binding() -> None:
    """An app with a single low-priority binding should have just the one binding."""
    async with LowAlphaBinding().run_test() as pilot:
        assert sorted(pilot.app._bindings.keys.keys()) == sorted(
            ["ctrl+c", "ctrl+backslash", "a"]
        )
        assert pilot.app._bindings.get_key("ctrl+c").priority is True
        assert pilot.app._bindings.get_key("a").priority is False


##############################################################################
# A non-default screen with a single alpha key binding.
#
# There's little point in testing a screen with no bindings added as that's
# pretty much the same as an app with a default screen (for the purposes of
# these tests). So, let's test a screen with a single alpha-key binding.


class ScreenWithBindings(Screen):
    """A screen with a simple alpha key binding."""

    BINDINGS = [Binding("a", "a", "a", priority=True)]


class AppWithScreenThatHasABinding(App[None]):
    """An app with no extra bindings but with a custom screen with a binding."""

    SCREENS = {"main": ScreenWithBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_app_screen_with_bindings() -> None:
    """Test a screen with a single key binding defined."""
    async with AppWithScreenThatHasABinding().run_test() as pilot:
        assert pilot.app.screen._bindings.get_key("a").priority is True


##############################################################################
# A non-default screen with a single low-priority alpha key binding.
#
# As above, but because Screen sets all keys as high priority by default, we
# want to be sure that if we set our keys in our subclass as low priority as
# default, they come through as such.


class ScreenWithLowBindings(Screen):
    """A screen with a simple low-priority alpha key binding."""

    BINDINGS = [Binding("a", "a", "a", priority=False)]


class AppWithScreenThatHasALowBinding(App[None]):
    """An app with no extra bindings but with a custom screen with a low-priority binding."""

    SCREENS = {"main": ScreenWithLowBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_app_screen_with_low_bindings() -> None:
    """Test a screen with a single low-priority key binding defined."""
    async with AppWithScreenThatHasALowBinding().run_test() as pilot:
        assert pilot.app.screen._bindings.get_key("a").priority is False


##############################################################################
# From here on in we're going to start simulating keystrokes to ensure that
# any bindings that are in place actually fire the correct actions. To help
# with this let's build a simple key/binding/action recorder base app.


class AppKeyRecorder(App[None]):
    """Base application class that can be used to record keystrokes."""

    ALPHAS = "abcxyz"
    """str: The alpha keys to test against."""

    ALL_KEYS = [*ALPHAS, *MOVEMENT_KEYS]
    """list[str]: All the test keys."""

    @staticmethod
    def make_bindings(action_prefix: str = "") -> list[Binding]:
        """Make the binding list for testing an app.

        Args:
            action_prefix (str, optional): An optional prefix for the action name.

        Returns:
            list[Binding]: The resulting list of bindings.
        """
        return [
            Binding(key, f"{action_prefix}record('{key}')", key)
            for key in [*AppKeyRecorder.ALPHAS, *MOVEMENT_KEYS]
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

    def all_recorded(self, marker_prefix: str = "") -> None:
        """Were all the bindings recorded from the presses?

        Args:
            marker_prefix (str, optional): An optional prefix for the result markers.
        """
        assert self.pressed_keys == [f"{marker_prefix}{key}" for key in self.ALL_KEYS]


##############################################################################
# An app with bindings for movement keys.
#
# Having gone through various permutations of testing for what bindings are
# seen to be in place, we now move on to adding bindings, invoking them and
# seeing what happens. First off let's start with an application that has
# bindings, both for an alpha key, and also for all of the movement keys.


class AppWithMovementKeysBound(AppKeyRecorder):
    """An application with bindings."""

    BINDINGS = AppKeyRecorder.make_bindings()


async def test_pressing_alpha_on_app() -> None:
    """Test that pressing the alpha key, when it's bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALPHAS)
        await pilot.pause()
        assert pilot.app.pressed_keys == [*AppKeyRecorder.ALPHAS]


async def test_pressing_movement_keys_app() -> None:
    """Test that pressing the movement keys, when they're bound on the app, results in an action fire."""
    async with AppWithMovementKeysBound().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        await pilot.pause()
        pilot.app.all_recorded()


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

    BINDINGS = AppKeyRecorder.make_bindings("local_")

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

        pilot.app.all_recorded("locally_")


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

    BINDINGS = AppKeyRecorder.make_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithNoBindings()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithNoBindings).focus()


class AppWithScreenWithBindingsWidgetNoBindings(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings."""

    SCREENS = {"main": ScreenWithMovementBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_focused_child_widget_with_movement_bindings_on_screen() -> None:
    """A focused child widget, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetNoBindings().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)

        pilot.app.all_recorded("screenly_")


##############################################################################
# A focused widget within a container within a screen that handles bindings.
#
# Similar again to the previous test, here we're wrapping an app around a
# non-default screen, which in turn wraps a container which wraps a widget
# that can have, and will have, focus. The issue here is that if the
# container isn't scrolling, especially if it's set up to just wrap a widget
# and do nothing else, it should not rob the screen of the binding hits.


class ScreenWithMovementBindingsAndContainerAroundWidget(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.make_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield Container(FocusableWidgetWithNoBindings())

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithNoBindings).focus()


class AppWithScreenWithBindingsWrappedWidgetNoBindings(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings."""

    SCREENS = {"main": ScreenWithMovementBindings}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_contained_focused_child_widget_with_movement_bindings_on_screen() -> (
    None
):
    """A contained focused child widget, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWrappedWidgetNoBindings().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)

        pilot.app.all_recorded("screenly_")


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

    BINDINGS = AppKeyRecorder.make_bindings("local_")

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

        pilot.app.all_recorded("locally_")


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


class FocusableWidgetWithNoBindingsNoInherit(
    Static, can_focus=True, inherit_bindings=False
):
    """A widget that can receive focus but has no bindings and doesn't inherit bindings."""


class ScreenWithMovementBindingsNoInheritChild(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.make_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithNoBindingsNoInherit()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithNoBindingsNoInherit).focus()


class AppWithScreenWithBindingsWidgetNoBindingsNoInherit(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings, child no-inherit."""

    SCREENS = {"main": ScreenWithMovementBindingsNoInheritChild}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_focused_child_widget_no_inherit_with_movement_bindings_on_screen() -> (
    None
):
    """A focused child widget, that doesn't inherit bindings, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetNoBindingsNoInherit().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)

        pilot.app.all_recorded("screenly_")


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


class FocusableWidgetWithEmptyBindingsNoInherit(
    Static, can_focus=True, inherit_bindings=False
):
    """A widget that can receive focus but has empty bindings and doesn't inherit bindings."""

    BINDINGS = []


class ScreenWithMovementBindingsNoInheritEmptyChild(Screen):
    """A screen that binds keys, including movement keys."""

    BINDINGS = AppKeyRecorder.make_bindings("screen_")

    async def action_screen_record(self, key: str) -> None:
        # Sneaky forward reference. Just for the purposes of testing.
        await self.app.action_record(f"screenly_{key}")

    def compose(self) -> ComposeResult:
        yield FocusableWidgetWithEmptyBindingsNoInherit()

    def on_mount(self) -> None:
        self.query_one(FocusableWidgetWithEmptyBindingsNoInherit).focus()


class AppWithScreenWithBindingsWidgetEmptyBindingsNoInherit(AppKeyRecorder):
    """An app with a non-default screen that handles movement key bindings, child no-inherit."""

    SCREENS = {"main": ScreenWithMovementBindingsNoInheritEmptyChild}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_focused_child_widget_no_inherit_empty_bindings_with_movement_bindings_on_screen() -> (
    None
):
    """A focused child widget, that doesn't inherit bindings and sets BINDINGS empty, with movement bindings in the screen, should trigger screen actions."""
    async with AppWithScreenWithBindingsWidgetEmptyBindingsNoInherit().run_test() as pilot:
        await pilot.press(*AppKeyRecorder.ALL_KEYS)
        pilot.app.all_recorded("screenly_")


##############################################################################
# Testing priority of overlapping bindings.
#
# Here we we'll have an app, screen, and a focused widget, along with a
# combination of overlapping bindings, each with different forms of
# priority, so we can check who wins where.
#
# Here are the permutations tested, with the expected winner:
#
# |-----|----------|----------|----------|--------|
# | Key | App      | Screen   | Widget   | Winner |
# |-----|----------|----------|----------|--------|
# | 0   |          |          |          | Widget |
# | A   | Priority |          |          | App    |
# | B   |          | Priority |          | Screen |
# | C   |          |          | Priority | Widget |
# | D   | Priority | Priority |          | App    |
# | E   | Priority |          | Priority | App    |
# | F   |          | Priority | Priority | Screen |


class PriorityOverlapWidget(Static, can_focus=True):
    """A focusable widget with a priority binding."""

    BINDINGS = [
        Binding("0", "app.record('widget_0')", "0", priority=False),
        Binding("a", "app.record('widget_a')", "a", priority=False),
        Binding("b", "app.record('widget_b')", "b", priority=False),
        Binding("c", "app.record('widget_c')", "c", priority=True),
        Binding("d", "app.record('widget_d')", "d", priority=False),
        Binding("e", "app.record('widget_e')", "e", priority=True),
        Binding("f", "app.record('widget_f')", "f", priority=True),
    ]


class PriorityOverlapScreen(Screen):
    """A screen with a priority binding."""

    BINDINGS = [
        Binding("0", "app.record('screen_0')", "0", priority=False),
        Binding("a", "app.record('screen_a')", "a", priority=False),
        Binding("b", "app.record('screen_b')", "b", priority=True),
        Binding("c", "app.record('screen_c')", "c", priority=False),
        Binding("d", "app.record('screen_d')", "c", priority=True),
        Binding("e", "app.record('screen_e')", "e", priority=False),
        Binding("f", "app.record('screen_f')", "f", priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield PriorityOverlapWidget()

    def on_mount(self) -> None:
        self.query_one(PriorityOverlapWidget).focus()


class PriorityOverlapApp(AppKeyRecorder):
    """An application with a priority binding."""

    BINDINGS = [
        Binding("0", "record('app_0')", "0", priority=False),
        Binding("a", "record('app_a')", "a", priority=True),
        Binding("b", "record('app_b')", "b", priority=False),
        Binding("c", "record('app_c')", "c", priority=False),
        Binding("d", "record('app_d')", "c", priority=True),
        Binding("e", "record('app_e')", "e", priority=True),
        Binding("f", "record('app_f')", "f", priority=False),
    ]

    SCREENS = {"main": PriorityOverlapScreen}

    def on_mount(self) -> None:
        self.push_screen("main")


async def test_overlapping_priority_bindings() -> None:
    """Test an app stack with overlapping bindings."""
    async with PriorityOverlapApp().run_test() as pilot:
        await pilot.press(*"0abcdef")
        assert pilot.app.pressed_keys == [
            "widget_0",
            "app_a",
            "screen_b",
            "widget_c",
            "app_d",
            "app_e",
            "screen_f",
        ]


async def test_skip_action() -> None:
    """Test that a binding may be skipped by an action raising SkipAction"""

    class Handle(Widget, can_focus=True):
        BINDINGS = [("t", "test('foo')", "Test")]

        def action_test(self, text: str) -> None:
            self.app.exit(text)

    no_handle_invoked = False

    class NoHandle(Widget, can_focus=True):
        BINDINGS = [("t", "test('bar')", "Test")]

        def action_test(self, text: str) -> bool:
            nonlocal no_handle_invoked
            no_handle_invoked = True
            raise SkipAction()

    class SkipApp(App):
        def compose(self) -> ComposeResult:
            yield Handle(NoHandle())

        def on_mount(self) -> None:
            self.query_one(NoHandle).focus()

    async with SkipApp().run_test() as pilot:
        # Check the NoHandle widget has focus
        assert pilot.app.query_one(NoHandle).has_focus
        # Press the "t" key
        await pilot.press("t")
        # Check the action on the no handle widget was called
        assert no_handle_invoked
        # Check the return value, confirming that the action on Handle was called
        assert pilot.app.return_value == "foo"
