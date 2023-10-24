import asyncio
import sys
import threading

import pytest

from textual import work
from textual.app import App, ComposeResult, ScreenStackError
from textual.events import MouseMove, MouseScrollDown, MouseScrollUp
from textual.geometry import Offset
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label
from textual.worker import NoActiveWorker

skip_py310 = pytest.mark.skipif(
    sys.version_info.minor == 10 and sys.version_info.major == 3,
    reason="segfault on py3.10",
)


async def test_screen_walk_children():
    """Test query only reports active screen."""

    class ScreensApp(App):
        pass

    app = ScreensApp()
    async with app.run_test() as pilot:
        screen1 = Screen()
        screen2 = Screen()
        pilot.app.push_screen(screen1)
        assert list(pilot.app.query("*")) == [screen1]
        pilot.app.push_screen(screen2)
        assert list(pilot.app.query("*")) == [screen2]


async def test_installed_screens():
    class ScreensApp(App):
        SCREENS = {
            "home": Screen,  # Screen type
            "one": Screen(),  # Screen instance
            "two": Screen,  # Callable[[], Screen]
        }

    app = ScreensApp()
    async with app.run_test() as pilot:
        pilot.app.push_screen("home")  # Instantiates and pushes the "home" screen
        pilot.app.push_screen("one")  # Pushes the pre-instantiated "one" screen
        pilot.app.push_screen("home")  # Pushes the single instance of "home" screen
        pilot.app.push_screen(
            "two"
        )  # Calls the callable, pushes returned Screen instance

        assert len(app.screen_stack) == 5
        assert app.screen_stack[1] is app.screen_stack[3]
        assert app.screen is app.screen_stack[4]
        assert isinstance(app.screen, Screen)
        assert app.is_screen_installed(app.screen)

        assert pilot.app.pop_screen()
        assert pilot.app.pop_screen()
        assert pilot.app.pop_screen()
        assert pilot.app.pop_screen()
        with pytest.raises(ScreenStackError):
            pilot.app.pop_screen()


async def test_screens():
    app = App()
    app._loop = asyncio.get_running_loop()
    app._thread_id = threading.get_ident()
    # There should be nothing in the children since the app hasn't run yet
    assert not app._nodes
    assert not app.children
    app._set_active()

    with pytest.raises(ScreenStackError):
        app.screen

    assert not app._installed_screens

    screen1 = Screen(name="screen1")
    screen2 = Screen(name="screen2")
    screen3 = Screen(name="screen3")

    # installs screens
    app.install_screen(screen1, "screen1")
    app.install_screen(screen2, "screen2")

    # Installing a screen does not add it to the DOM
    assert not app._nodes
    assert not app.children

    # Check they are installed
    assert app.is_screen_installed("screen1")
    assert app.is_screen_installed("screen2")

    assert app.get_screen("screen1") is screen1
    with pytest.raises(KeyError):
        app.get_screen("foo")

    # Check screen3 is not installed
    assert not app.is_screen_installed("screen3")

    # Installs screen3
    app.install_screen(screen3, "screen3")
    # Confirm installed
    assert app.is_screen_installed("screen3")

    # Check screen stack is empty
    assert app.screen_stack == []
    # Push a screen
    app.push_screen("screen1")
    # Check it is on the stack
    assert app.screen_stack == [screen1]
    # Check it is current
    assert app.screen is screen1
    # There should be one item in the children view
    assert app.children == (screen1,)

    # Switch to another screen
    app.switch_screen("screen2")
    # Check it has changed the stack and that it is current
    assert app.screen_stack == [screen2]
    assert app.screen is screen2
    assert app.children == (screen2,)

    # Push another screen
    app.push_screen("screen3")
    assert app.screen_stack == [screen2, screen3]
    assert app.screen is screen3
    # Only the current screen is in children
    assert app.children == (screen3,)

    # Pop a screen
    assert app.pop_screen() is screen3
    assert app.screen is screen2
    assert app.screen_stack == [screen2]

    # Uninstall screens
    app.uninstall_screen(screen1)
    assert not app.is_screen_installed(screen1)
    app.uninstall_screen("screen3")
    assert not app.is_screen_installed(screen1)

    # Check we can't uninstall a screen on the stack
    with pytest.raises(ScreenStackError):
        app.uninstall_screen(screen2)

    # Check we can't pop last screen
    with pytest.raises(ScreenStackError):
        app.pop_screen()

    screen1.remove()
    screen2.remove()
    screen3.remove()
    await app._shutdown()


async def test_auto_focus_on_screen_if_app_auto_focus_is_none():
    """Setting app.AUTO_FOCUS = `None` means it is not taken into consideration."""

    class MyScreen(Screen[None]):
        def compose(self):
            yield Button()
            yield Input(id="one")
            yield Input(id="two")

    class MyApp(App[None]):
        AUTO_FOCUS = None

    app = MyApp()
    async with app.run_test():
        MyScreen.AUTO_FOCUS = "*"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Button)
        app.pop_screen()

        MyScreen.AUTO_FOCUS = None
        await app.push_screen(MyScreen())
        assert app.focused is None
        app.pop_screen()

        MyScreen.AUTO_FOCUS = "Input"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Input)
        assert app.focused.id == "one"
        app.pop_screen()

        MyScreen.AUTO_FOCUS = "#two"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Input)
        assert app.focused.id == "two"

        # If we push and pop another screen, focus should be preserved for #two.
        MyScreen.AUTO_FOCUS = None
        await app.push_screen(MyScreen())
        assert app.focused is None
        app.pop_screen()
        assert app.focused.id == "two"


async def test_auto_focus_on_screen_if_app_auto_focus_is_disabled():
    """Setting app.AUTO_FOCUS = `None` means it is not taken into consideration."""

    class MyScreen(Screen[None]):
        def compose(self):
            yield Button()
            yield Input(id="one")
            yield Input(id="two")

    class MyApp(App[None]):
        AUTO_FOCUS = ""

    app = MyApp()
    async with app.run_test():
        MyScreen.AUTO_FOCUS = "*"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Button)
        app.pop_screen()

        MyScreen.AUTO_FOCUS = None
        await app.push_screen(MyScreen())
        assert app.focused is None
        app.pop_screen()

        MyScreen.AUTO_FOCUS = "Input"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Input)
        assert app.focused.id == "one"
        app.pop_screen()

        MyScreen.AUTO_FOCUS = "#two"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Input)
        assert app.focused.id == "two"

        # If we push and pop another screen, focus should be preserved for #two.
        MyScreen.AUTO_FOCUS = None
        await app.push_screen(MyScreen())
        assert app.focused is None
        app.pop_screen()
        assert app.focused.id == "two"


async def test_auto_focus_inheritance():
    """Setting app.AUTO_FOCUS = `None` means it is not taken into consideration."""

    class MyScreen(Screen[None]):
        def compose(self):
            yield Button()
            yield Input(id="one")
            yield Input(id="two")

    class MyApp(App[None]):
        pass

    app = MyApp()
    async with app.run_test():
        MyApp.AUTO_FOCUS = "Input"
        MyScreen.AUTO_FOCUS = "*"
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Button)
        app.pop_screen()

        MyScreen.AUTO_FOCUS = None
        await app.push_screen(MyScreen())
        assert isinstance(app.focused, Input)
        app.pop_screen()

        MyScreen.AUTO_FOCUS = ""
        await app.push_screen(MyScreen())
        assert app.focused is None
        app.pop_screen()


async def test_auto_focus_skips_non_focusable_widgets():
    class MyScreen(Screen[None]):
        def compose(self):
            yield Label()
            yield Button()

    class MyApp(App[None]):
        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test():
        assert app.focused is not None
        assert isinstance(app.focused, Button)


async def test_dismiss_non_top_screen():
    class MyApp(App[None]):
        async def key_p(self) -> None:
            self.bottom, top = Screen(), Screen()
            await self.push_screen(self.bottom)
            await self.push_screen(top)

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("p")
        with pytest.raises(ScreenStackError):
            app.bottom.dismiss()


async def test_dismiss_action():
    class ConfirmScreen(Screen[bool]):
        BINDINGS = [("y", "dismiss(True)", "Dismiss")]

    class MyApp(App[None]):
        bingo = False

        def on_mount(self) -> None:
            self.push_screen(ConfirmScreen(), callback=self.callback)

        def callback(self, result: bool) -> None:
            self.bingo = result

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("y")
        assert app.bingo


async def test_switch_screen_no_op():
    """Regression test for https://github.com/Textualize/textual/issues/2650"""

    class MyScreen(Screen):
        pass

    class MyApp(App[None]):
        SCREENS = {"screen": MyScreen()}

        def on_mount(self):
            self.push_screen("screen")

    app = MyApp()
    async with app.run_test():
        screen_id = id(app.screen)
        app.switch_screen("screen")
        assert screen_id == id(app.screen)
        app.switch_screen("screen")
        assert screen_id == id(app.screen)


async def test_switch_screen_updates_results_callback_stack():
    """Regression test for https://github.com/Textualize/textual/issues/2650"""

    class ScreenA(Screen):
        pass

    class ScreenB(Screen):
        pass

    class MyApp(App[None]):
        SCREENS = {
            "a": ScreenA(),
            "b": ScreenB(),
        }

        def callback(self, _):
            return 42

        def on_mount(self):
            self.push_screen("a", self.callback)

    app = MyApp()
    async with app.run_test():
        assert len(app.screen._result_callbacks) == 1
        assert app.screen._result_callbacks[-1].callback(None) == 42

        app.switch_screen("b")
        assert len(app.screen._result_callbacks) == 1
        assert app.screen._result_callbacks[-1].callback is None


async def test_screen_receives_mouse_move_events():
    class MouseMoveRecordingScreen(Screen):
        mouse_events = []

        def on_mouse_move(self, event: MouseMove) -> None:
            MouseMoveRecordingScreen.mouse_events.append(event)

    class SimpleApp(App[None]):
        SCREENS = {"a": MouseMoveRecordingScreen()}

        def on_mount(self):
            self.push_screen("a")

    mouse_offset = Offset(1, 1)

    async with SimpleApp().run_test() as pilot:
        await pilot.hover(None, mouse_offset)

    assert len(MouseMoveRecordingScreen.mouse_events) == 1
    mouse_event = MouseMoveRecordingScreen.mouse_events[0]
    assert mouse_event.x, mouse_event.y == mouse_offset


async def test_mouse_move_event_bubbles_to_screen_from_widget():
    class MouseMoveRecordingScreen(Screen):
        mouse_events = []

        DEFAULT_CSS = """
        Label {
            offset: 10 10;
        }
        """

        def compose(self) -> ComposeResult:
            yield Label("Any label")

        def on_mouse_move(self, event: MouseMove) -> None:
            MouseMoveRecordingScreen.mouse_events.append(event)

    class SimpleApp(App[None]):
        SCREENS = {"a": MouseMoveRecordingScreen()}

        def on_mount(self):
            self.push_screen("a")

    label_offset = Offset(10, 10)
    mouse_offset = Offset(1, 1)

    async with SimpleApp().run_test() as pilot:
        await pilot.hover(Label, mouse_offset)

    assert len(MouseMoveRecordingScreen.mouse_events) == 1
    mouse_event = MouseMoveRecordingScreen.mouse_events[0]
    assert mouse_event.x, mouse_event.y == (
        label_offset.x + mouse_offset.x,
        label_offset.y + mouse_offset.y,
    )


async def test_push_screen_wait_for_dismiss() -> None:
    """Test push_screen returns result."""

    class QuitScreen(Screen[bool]):
        BINDINGS = [
            ("y", "quit(True)"),
            ("n", "quit(False)"),
        ]

        def action_quit(self, quit: bool) -> None:
            self.dismiss(quit)

    results: list[bool] = []

    class ScreensApp(App):
        BINDINGS = [("x", "exit")]

        @work
        async def action_exit(self) -> None:
            result = await self.push_screen(QuitScreen(), wait_for_dismiss=True)
            results.append(result)

    app = ScreensApp()
    # Press X to exit, then Y to dismiss, expect True result
    async with app.run_test() as pilot:
        await pilot.press("x", "y")
    assert results == [True]

    results.clear()
    app = ScreensApp()
    # Press X to exit, then N to dismiss, expect False result
    async with app.run_test() as pilot:
        await pilot.press("x", "n")
    assert results == [False]


async def test_push_screen_wait_for_dismiss_no_worker() -> None:
    """Test wait_for_dismiss raises NoActiveWorker when not using workers."""

    class QuitScreen(Screen[bool]):
        BINDINGS = [
            ("y", "quit(True)"),
            ("n", "quit(False)"),
        ]

        def action_quit(self, quit: bool) -> None:
            self.dismiss(quit)

    results: list[bool] = []

    class ScreensApp(App):
        BINDINGS = [("x", "exit")]

        async def action_exit(self) -> None:
            result = await self.push_screen(QuitScreen(), wait_for_dismiss=True)
            results.append(result)

    app = ScreensApp()
    # using `wait_for_dismiss` outside of a worker should raise NoActiveWorker
    with pytest.raises(NoActiveWorker):
        async with app.run_test() as pilot:
            await pilot.press("x", "y")
