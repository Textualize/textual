from __future__ import annotations
import os

import asyncio
import platform
from typing import Any, Callable, ClassVar, Type, TypeVar
import warnings

from rich.control import Control
import rich.repr
from rich.screen import Screen
from rich.console import Console, RenderableType
from rich.measure import Measurement
from rich.traceback import Traceback

from . import events
from . import actions
from ._animator import Animator
from .binding import Bindings, NoBinding
from .geometry import Offset, Region
from . import log
from ._callback import invoke
from ._context import active_app
from ._event_broker import extract_handler_actions, NoHandler
from .driver import Driver
from .layouts.dock import DockLayout, Dock
from .message_pump import MessagePump
from ._profile import timer
from .view import View
from .views import DockView
from .widget import Widget, Reactive

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"

# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)


LayoutDefinition = "dict[str, Any]"

ViewType = TypeVar("ViewType", bound=View)

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


class ActionError(Exception):
    pass


@rich.repr.auto
class App(MessagePump):
    """The base class for Textual Applications"""

    KEYS: ClassVar[dict[str, str]] = {}

    def __init__(
        self,
        screen: bool = True,
        driver_class: Type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
    ):
        """The Textual Application base class

        Args:
            console (Console, optional): A Rich Console. Defaults to None.
            screen (bool, optional): Enable full-screen application mode. Defaults to True.
            driver_class (Type[Driver], optional): Driver class, or None to use default. Defaults to None.
            title (str, optional): Title of the application. Defaults to "Textual Application".
        """
        self.console = Console()
        self.error_console = Console(stderr=True)
        self._screen = screen
        self.driver_class = driver_class or self.get_driver_class()
        self._title = title
        self._layout = DockLayout()
        self._view_stack: list[DockView] = []
        self.children: set[MessagePump] = set()

        self.focused: Widget | None = None
        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._docks: list[Dock] = []
        self._action_targets = {"app", "view"}
        self._animator = Animator(self)
        self.animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)
        self.bindings = Bindings()
        self._title = title

        self.log_file = open(log, "wt") if log else None
        self.log_verbosity = log_verbosity

        self.bindings.bind("ctrl+c", "quit", show=False, allow_forward=False)
        self._refresh_required = False

        super().__init__()

    title: Reactive[str] = Reactive("Textual")
    sub_title: Reactive[str] = Reactive("")
    background: Reactive[str] = Reactive("black")

    def get_driver_class(self) -> Type[Driver]:
        """Get a driver class for this platform.

        Called by the constructor.

        Returns:
            Driver: A Driver class which manages input and display.
        """
        if WINDOWS:
            from .drivers.windows_driver import WindowsDriver

            driver_class = WindowsDriver
        else:
            from .drivers.linux_driver import LinuxDriver

            driver_class = LinuxDriver
        return driver_class

    def __rich_repr__(self) -> rich.repr.Result:
        yield "title", self.title

    def __rich__(self) -> RenderableType:
        return self.view

    @property
    def animator(self) -> Animator:
        return self._animator

    @property
    def view(self) -> DockView:
        return self._view_stack[-1]

    def log(self, *args: Any, verbosity: int = 1, **kwargs) -> None:
        """Write to logs.

        Args:
            *args (Any): Positional arguments are converted to string and written to logs.
            verbosity (int, optional): Verbosity level 0-3. Defaults to 1.
        """
        try:
            if self.log_file and verbosity <= self.log_verbosity:
                output = f" ".join(str(arg) for arg in args)
                if kwargs:
                    key_values = " ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                    output = " ".join((output, key_values))
                self.log_file.write(output + "\n")
                self.log_file.flush()
        except Exception:
            pass

    async def bind(
        self,
        keys: str,
        action: str,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
    ) -> None:
        """Bind a key to an action.

        Args:
            keys (str): A comma separated list of keys, i.e.
            action (str): Action to bind to.
            description (str, optional): Short description of action. Defaults to "".
            show (bool, optional): Show key in UI. Defaults to True.
            key_display (str, optional): Replacement text for key, or None to use default. Defaults to None.
        """
        self.bindings.bind(
            keys, action, description, show=show, key_display=key_display
        )

    @classmethod
    def run(
        cls,
        console: Console = None,
        screen: bool = True,
        driver: Type[Driver] = None,
        **kwargs,
    ):
        """Run the app.

        Args:
            console (Console, optional): Console object. Defaults to None.
            screen (bool, optional): Enable application mode. Defaults to True.
            driver (Type[Driver], optional): Driver class or None for default. Defaults to None.
        """

        async def run_app() -> None:
            app = cls(screen=screen, driver_class=driver, **kwargs)
            await app.process_messages()

        asyncio.run(run_app())

    async def push_view(self, view: ViewType) -> ViewType:
        self.register(view, self)
        self._view_stack.append(view)
        return view

    async def set_focus(self, widget: Widget | None) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget (Widget): [description]
        """
        log("set_focus", widget)
        if widget == self.focused:
            # Widget is already focused
            return

        if widget is None:
            if self.focused is not None:
                focused = self.focused
                self.focused = None
                await focused.post_message(events.Blur(self))
        elif widget.can_focus:
            if self.focused is not None:
                await self.focused.post_message(events.Blur(self))
            if widget is not None and self.focused != widget:
                self.focused = widget
                await widget.post_message(events.Focus(self))

    async def set_mouse_over(self, widget: Widget | None) -> None:
        if widget is None:
            if self.mouse_over is not None:
                try:
                    await self.mouse_over.post_message(events.Leave(self))
                finally:
                    self.mouse_over = None
        else:
            if self.mouse_over != widget:
                try:
                    if self.mouse_over is not None:
                        await self.mouse_over.forward_event(events.Leave(self))
                    if widget is not None:
                        await widget.forward_event(events.Enter(self))
                finally:
                    self.mouse_over = widget

    async def capture_mouse(self, widget: Widget | None) -> None:
        """Send all mouse events to the given widget, disable mouse capture.

        Args:
            widget (Widget | None): If a widget, capture mouse event, or None to end mouse capture.
        """
        if widget == self.mouse_captured:
            return
        if self.mouse_captured is not None:
            await self.mouse_captured.post_message(
                events.MouseRelease(self, self.mouse_position)
            )
        self.mouse_captured = widget
        if widget is not None:
            await widget.post_message(events.MouseCapture(self, self.mouse_position))

    def panic(self, *renderables: RenderableType) -> None:
        """Exits the app with a traceback.

        Args:
            traceback (Traceback, optional): Rich Traceback object or None to generate one
                for the most recent exception. Defaults to None.
        """

        if not renderables:
            renderables = (
                Traceback(show_locals=True, width=None, locals_max_length=5),
            )
        self._exit_renderables.extend(renderables)
        self.close_messages_no_wait()

    async def process_messages(self) -> None:
        active_app.set(self)

        log("---")
        log(f"driver={self.driver_class}")

        load_event = events.Load(sender=self)
        await self.dispatch_message(load_event)
        await self.post_message(events.Mount(self))
        await self.push_view(DockView())

        # Wait for the load event to be processed, so we don't go in to application mode beforehand
        await load_event.wait()

        driver = self._driver = self.driver_class(self.console, self)
        try:
            driver.start_application_mode()
        except Exception:
            self.console.print_exception()
        else:
            try:
                self.console = Console()
                self.title = self._title
                self.refresh()
                await self.animator.start()
                await super().process_messages()
                log("PROCESS END")
                await self.animator.stop()
                await self.close_all()

            except Exception:
                self.panic()
            finally:
                driver.stop_application_mode()
                if self._exit_renderables:
                    for renderable in self._exit_renderables:
                        self.error_console.print(renderable)
                if self.log_file is not None:
                    self.log_file.close()

    def register(self, child: MessagePump, parent: MessagePump) -> bool:
        if child not in self.children:
            self.children.add(child)
            child.set_parent(parent)
            child.start_messages()
            child.post_message_no_wait(events.Mount(sender=parent))
            return True
        return False

    async def close_all(self) -> None:
        while self.children:
            child = self.children.pop()
            await child.close_messages()

    async def remove(self, child: MessagePump) -> None:
        self.children.remove(child)

    async def shutdown(self):
        driver = self._driver
        assert driver is not None
        driver.disable_input()
        await self.close_messages()

    def refresh(self, repaint: bool = True, layout: bool = False) -> None:
        sync_available = (
            os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal" and not WINDOWS
        )
        if not self._closed:
            console = self.console
            try:
                if sync_available:
                    console.file.write("\x1bP=1s\x1b\\")
                console.print(Screen(Control.home(), self.view, Control.home()))
                if sync_available:
                    console.file.write("\x1bP=2s\x1b\\")
                console.file.flush()
            except Exception:
                self.panic()

    def display(self, renderable: RenderableType) -> None:
        sync_available = os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal"
        if not self._closed:
            console = self.console
            try:
                console.print(renderable)
            except Exception:
                self.panic()

    def measure(self, renderable: RenderableType, max_width=100_000) -> int:
        """Get the optimal width for a widget or renderable.

        Args:
            renderable (RenderableType): A renderable (including Widget)
            max_width ([type], optional): Maximum width. Defaults to 100_000.

        Returns:
            int: Number of cells required to render.
        """
        measurement = Measurement.get(
            self.console, self.console.options.update(max_width=max_width), renderable
        )
        return measurement.maximum

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget under the given coordinates.

        Args:
            x (int): X Coord.
            y (int): Y Coord.

        Returns:
            tuple[Widget, Region]: The widget and the widget's screen region.
        """
        return self.view.get_widget_at(x, y)

    async def press(self, key: str) -> bool:
        """Handle a key press.

        Args:
            key (str): A key

        Returns:
            bool: True if the key was handled by a binding, otherwise False
        """
        try:
            binding = self.bindings.get_key(key)
        except NoBinding:
            return False
        else:
            await self.action(binding.action)
        return True

    async def on_event(self, event: events.Event) -> None:
        # Handle input events that haven't been forwarded
        # If the event has been forwarded it may have bubbled up back to the App
        if isinstance(event, events.InputEvent) and not event.is_forwarded:
            if isinstance(event, events.MouseEvent):
                # Record current mouse position on App
                self.mouse_position = Offset(event.x, event.y)
            if isinstance(event, events.Key) and self.focused is not None:
                # Key events are sent direct to focused widget
                if self.bindings.allow_forward(event.key):
                    await self.focused.forward_event(event)
                else:
                    # Key has allow_forward=False which disallows forward to focused widget
                    await super().on_event(event)
            else:
                # Forward the event to the view
                await self.view.forward_event(event)
        else:
            await super().on_event(event)

    async def action(
        self,
        action: str,
        default_namespace: object | None = None,
        modifiers: set[str] | None = None,
    ) -> None:
        """Perform an action.

        Args:
            action (str): Action encoded in a string.
        """
        target, params = actions.parse(action)
        if "." in target:
            destination, action_name = target.split(".", 1)
            if destination not in self._action_targets:
                raise ActionError(f"Action namespace {destination} is not known")
            action_target = getattr(self, destination)
        else:
            action_target = default_namespace or self
            action_name = target

        log("ACTION", action_target, action_name)
        await self.dispatch_action(action_target, action_name, params)

    async def dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> None:
        _rich_traceback_guard = True
        method_name = f"action_{action_name}"
        method = getattr(namespace, method_name, None)
        if callable(method):
            await invoke(method, *params)

    async def broker_event(
        self, event_name: str, event: events.Event, default_namespace: object | None
    ) -> bool:
        event.stop()
        try:
            style = getattr(event, "style")
        except AttributeError:
            return False
        try:
            modifiers, action = extract_handler_actions(event_name, style.meta)
        except NoHandler:
            return False
        if isinstance(action, str):
            await self.action(
                action, default_namespace=default_namespace, modifiers=modifiers
            )
        elif isinstance(action, Callable):
            await action()
        else:
            return False
        return True

    async def on_key(self, event: events.Key) -> None:
        await self.press(event.key)

    async def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log("shutdown request")
        await self.close_messages()

    async def on_resize(self, event: events.Resize) -> None:
        await self.view.post_message(event)

    async def action_press(self, key: str) -> None:
        await self.press(key)

    async def action_quit(self) -> None:
        await self.shutdown()

    async def action_bang(self) -> None:
        1 / 0

    async def action_bell(self) -> None:
        self.console.bell()


if __name__ == "__main__":
    import asyncio
    from logging import FileHandler

    from rich.panel import Panel

    from .widgets import Header
    from .widgets import Footer

    from .widgets import Placeholder
    from .scrollbar import ScrollBar

    from rich.markdown import Markdown

    # from .widgets.scroll_view import ScrollView

    import os

    class MyApp(App):
        """Just a test app."""

        async def on_load(self, event: events.Load) -> None:
            await self.bind("ctrl+c", "quit", show=False)
            await self.bind("q", "quit", "Quit")
            await self.bind("x", "bang", "Test error handling")
            await self.bind("b", "toggle_sidebar", "Toggle sidebar")

        show_bar: Reactive[bool] = Reactive(False)

        async def watch_show_bar(self, show_bar: bool) -> None:
            self.animator.animate(self.bar, "layout_offset_x", 0 if show_bar else -40)

        async def action_toggle_sidebar(self) -> None:
            self.show_bar = not self.show_bar

        async def on_mount(self, event: events.Mount) -> None:

            view = await self.push_view(DockView())

            header = Header()
            footer = Footer()
            self.bar = Placeholder(name="left")

            await view.dock(header, edge="top")
            await view.dock(footer, edge="bottom")
            await view.dock(self.bar, edge="left", size=40, z=1)
            self.bar.layout_offset_x = -40

            sub_view = DockView()
            await sub_view.dock(Placeholder(), Placeholder(), edge="top")
            await view.dock(sub_view, edge="left")

    MyApp.run(log="textual.log")
