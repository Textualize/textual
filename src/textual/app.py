from __future__ import annotations

import asyncio
import inspect
import os
import platform
import sys
import warnings
from asyncio import AbstractEventLoop
from contextlib import redirect_stdout
from time import perf_counter
from typing import Any, Iterable, Type, TYPE_CHECKING

import rich
import rich.repr
from rich.console import Console, RenderableType
from rich.control import Control
from rich.measure import Measurement
from rich.screen import Screen as ScreenRenderable
from rich.segment import Segments
from rich.traceback import Traceback

from . import actions
from . import events
from . import log
from . import messages
from ._animator import Animator
from ._callback import invoke
from ._context import active_app
from ._event_broker import extract_handler_actions, NoHandler
from ._profile import timer
from .binding import Bindings, NoBinding
from .css.stylesheet import Stylesheet, StylesheetError
from .design import ColorSystem
from .devtools.client import DevtoolsClient, DevtoolsConnectionError, DevtoolsLog
from .devtools.redirect_output import StdoutRedirector
from .dom import DOMNode
from .driver import Driver
from .file_monitor import FileMonitor
from .geometry import Offset, Region, Size
from .layouts.dock import Dock
from .message_pump import MessagePump
from .reactive import Reactive
from .screen import Screen
from .widget import Widget

if TYPE_CHECKING:
    from .css.query import DOMQuery

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"

# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)

LayoutDefinition = "dict[str, Any]"


DEFAULT_COLORS = ColorSystem(
    primary="#406e8e",
    secondary="#ffa62b",
    warning="#ffa62b",
    error="#ba3c5b",
    success="#6d9f71",
    accent="#ffa62b",
    system="#5a4599",
)


class AppError(Exception):
    pass


class ActionError(Exception):
    pass


@rich.repr.auto
class App(DOMNode):
    """The base class for Textual Applications"""

    css = ""

    def __init__(
        self,
        screen: bool = True,
        driver_class: Type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
        css_file: str | None = None,
        css: str | None = None,
        watch_css: bool = True,
    ):
        """The Textual Application base class

        Args:
            console (Console, optional): A Rich Console. Defaults to None.
            screen (bool, optional): Enable full-screen application mode. Defaults to True.
            driver_class (Type[Driver], optional): Driver class, or None to use default. Defaults to None.
            title (str, optional): Title of the application. Defaults to "Textual Application".
        """
        self.console = Console(markup=False, highlight=False, emoji=False)
        self.error_console = Console(markup=False, stderr=True)
        self._screen = screen
        self.driver_class = driver_class or self.get_driver_class()
        self._title = title
        self._screen_stack: list[Screen] = []

        self.focused: Widget | None = None
        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._docks: list[Dock] = []
        self._action_targets = {"app", "screen"}
        self._animator = Animator(self)
        self.animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)
        self.bindings = Bindings()
        self._title = title

        self._log_console: Console | None = None
        if log:
            self._log_file = open(log, "wt")
            self._log_console = Console(
                file=self._log_file,
                markup=False,
                emoji=False,
                highlight=False,
                width=100,
            )
        else:
            self._log_console = None
            self._log_file = None

        self.log_verbosity = log_verbosity

        self.bindings.bind("ctrl+c", "quit", show=False, allow_forward=False)
        self._refresh_required = False

        self.design = DEFAULT_COLORS

        self.stylesheet = Stylesheet(variables=self.get_css_variables())
        self._require_styles_update = False

        self.css_file = css_file
        self.css_monitor = (
            FileMonitor(css_file, self._on_css_change)
            if (watch_css and css_file)
            else None
        )
        if css is not None:
            self.css = css

        self.registry: set[MessagePump] = set()

        self.devtools = DevtoolsClient()

        super().__init__()

    title: Reactive[str] = Reactive("Textual")
    sub_title: Reactive[str] = Reactive("")
    background: Reactive[str] = Reactive("black")
    dark = Reactive(False)

    def get_css_variables(self) -> dict[str, str]:
        """Get a mapping of variables used to pre-populate CSS.

        Returns:
            dict[str, str]: A mapping of variable name to value.
        """
        variables = self.design.generate(self.dark)
        return variables

    def watch_dark(self, dark: bool) -> None:
        """Watches the dark bool."""
        self.screen.dark = dark
        self.refresh_css()

    def get_driver_class(self) -> Type[Driver]:
        """Get a driver class for this platform.

        Called by the constructor.

        Returns:
            Driver: A Driver class which manages input and display.
        """
        driver_class: Type[Driver]
        if WINDOWS:
            from .drivers.windows_driver import WindowsDriver

            driver_class = WindowsDriver
        else:
            from .drivers.linux_driver import LinuxDriver

            driver_class = LinuxDriver
        return driver_class

    def __rich_repr__(self) -> rich.repr.Result:
        yield "title", self.title

    @property
    def animator(self) -> Animator:
        return self._animator

    @property
    def screen(self) -> Screen:
        return self._screen_stack[-1]

    @property
    def css_type(self) -> str:
        return "app"

    @property
    def size(self) -> Size:
        return Size(*self.console.size)

    def log(
        self,
        *objects: Any,
        verbosity: int = 1,
        _textual_calling_frame: inspect.FrameInfo | None = None,
        **kwargs,
    ) -> None:
        """Write to logs.

        Args:
            *objects (Any): Positional arguments are converted to string and written to logs.
            verbosity (int, optional): Verbosity level 0-3. Defaults to 1.
            _textual_calling_frame (inspect.FrameInfo | None): The frame info to include in
                the log message sent to the devtools server.
        """
        if verbosity > self.log_verbosity:
            return

        if self.devtools.is_connected and not _textual_calling_frame:
            _textual_calling_frame = inspect.stack()[1]

        try:
            if len(objects) == 1 and not kwargs:
                if self._log_console is not None:
                    self._log_console.print(objects[0])
                if self.devtools.is_connected:
                    self.devtools.log(
                        DevtoolsLog(objects, caller=_textual_calling_frame)
                    )
            else:
                output = " ".join(str(arg) for arg in objects)
                if kwargs:
                    key_values = " ".join(
                        f"{key}={value}" for key, value in kwargs.items()
                    )
                    output = " ".join((output, key_values))
                if self._log_console is not None:
                    self._log_console.print(output, soft_wrap=True)
                if self.devtools.is_connected:
                    self.devtools.log(
                        DevtoolsLog(output, caller=_textual_calling_frame)
                    )
        except Exception:
            pass

    def bind(
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
        console: Console | None = None,
        screen: bool = True,
        driver: Type[Driver] | None = None,
        loop: AbstractEventLoop | None = None,
        **kwargs,
    ):
        """Run the app.

        Args:
            console (Console, optional): Console object. Defaults to None.
            screen (bool, optional): Enable application mode. Defaults to True.
            driver (Type[Driver], optional): Driver class or None for default. Defaults to None.
            loop (AbstractEventLoop): Event loop to run the application on. If not specified, uvloop will be used.
        """

        async def run_app() -> None:
            app = cls(screen=screen, driver_class=driver, **kwargs)
            await app.process_messages()

        if loop:
            asyncio.set_event_loop(loop)
        else:
            try:
                import uvloop
            except ImportError:
                pass
            else:
                asyncio.set_event_loop(uvloop.new_event_loop())

        event_loop = asyncio.get_event_loop()
        try:
            asyncio.run(run_app())
        finally:
            event_loop.close()

    async def _on_css_change(self) -> None:
        """Called when the CSS changes (if watch_css is True)."""
        if self.css_file is not None:
            stylesheet = Stylesheet(variables=self.get_css_variables())
            try:
                time = perf_counter()
                stylesheet.read(self.css_file)
                elapsed = (perf_counter() - time) * 1000
                self.log(f"loaded {self.css_file} in {elapsed:.0f}ms")
            except Exception as error:
                # TODO: Catch specific exceptions
                self.console.bell()
                self.log(error)
            else:
                self.reset_styles()
                self.stylesheet = stylesheet
                self.stylesheet.update(self)
                self.screen.refresh(layout=True)

    def query(self, selector: str | None = None) -> DOMQuery:
        """Get a DOM query in the current screen.

        Args:
            selector (str, optional): A CSS selector or `None` for all nodes. Defaults to None.

        Returns:
            DOMQuery: A query object.
        """
        from .css.query import DOMQuery

        return DOMQuery(self.screen, selector)

    def get_child(self, id: str) -> DOMNode:
        """Shorthand for self.screen.get_child(id: str)
        Returns the first child (immediate descendent) of this DOMNode
        with the given ID.

        Args:
            id (str): The ID of the node to search for.

        Returns:
            DOMNode: The first child of this node with the specified ID.
        """
        return self.screen.get_child(id)

    def update_styles(self) -> None:
        """Request update of styles.

        Should be called whenever CSS classes / pseudo classes change.

        """
        self._require_styles_update = True
        self.check_idle()

    def mount(self, *anon_widgets: Widget, **widgets: Widget) -> None:
        self.register(self.screen, *anon_widgets, **widgets)
        self.screen.refresh()

    async def push_screen(self, screen: Screen) -> Screen:
        self._screen_stack.append(screen)
        return screen

    async def set_focus(self, widget: Widget | None) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget (Widget): [description]
        """
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
        """Exits the app then displays a message.

        Args:
            *renderables (RenderableType, optional): Rich renderables to display on exit.
        """

        prerendered = [
            Segments(self.console.render(renderable, self.console.options))
            for renderable in renderables
        ]

        self._exit_renderables.extend(prerendered)
        self.close_messages_no_wait()

    def on_exception(self, error: Exception) -> None:
        """Called with an unhandled exception.

        Args:
            error (Exception): An exception instance.
        """
        if hasattr(error, "__rich__"):
            # Exception has a rich method, so we can defer to that for the rendering
            self.panic(error)
        else:
            # Use default exception rendering
            self.fatal_error()

    def fatal_error(self) -> None:
        """Exits the app after an unhandled exception."""
        traceback = Traceback(
            show_locals=True, width=None, locals_max_length=5, suppress=[rich]
        )
        self._exit_renderables.append(
            Segments(self.console.render(traceback, self.console.options))
        )
        self.close_messages_no_wait()

    def _print_error_renderables(self) -> None:
        for renderable in self._exit_renderables:
            self.error_console.print(renderable)
        self._exit_renderables.clear()

    async def process_messages(self) -> None:
        active_app.set(self)
        log("---")
        log(f"driver={self.driver_class}")

        if os.getenv("TEXTUAL_DEVTOOLS") == "1":
            try:
                await self.devtools.connect()
                if self._log_console:
                    self._log_console.print(
                        f"Connected to devtools ({self.devtools.url})"
                    )
            except DevtoolsConnectionError:
                if self._log_console:
                    self._log_console.print(
                        f"Couldn't connect to devtools ({self.devtools.url})"
                    )
        try:
            if self.css_file is not None:
                self.stylesheet.read(self.css_file)
            if self.css is not None:
                self.stylesheet.parse(self.css, path=f"<{self.__class__.__name__}>")
        except Exception as error:
            self.on_exception(error)
            self._print_error_renderables()
            return

        if self.css_monitor:
            self.set_interval(0.5, self.css_monitor, name="css monitor")
            self.log("started", self.css_monitor)

        self._running = True
        try:
            load_event = events.Load(sender=self)
            await self.dispatch_message(load_event)
            # Wait for the load event to be processed, so we don't go in to application mode beforehand
            # await load_event.wait()

            driver = self._driver = self.driver_class(self.console, self)
            driver.start_application_mode()
            try:
                mount_event = events.Mount(sender=self)
                await self.dispatch_message(mount_event)

                self.console = Console(file=sys.__stdout__)
                self.title = self._title
                self.refresh()
                await self.animator.start()

                with redirect_stdout(StdoutRedirector(self.devtools, self._log_file)):  # type: ignore
                    await super().process_messages()
                    log("Message processing stopped")
                    with timer("animator.stop()"):
                        await self.animator.stop()
                    with timer("self.close_all()"):
                        await self.close_all()
            finally:
                driver.stop_application_mode()
        except Exception as error:
            self.on_exception(error)
        finally:
            self._running = False
            if self._exit_renderables:
                self._print_error_renderables()
            if self.devtools.is_connected:
                await self._disconnect_devtools()
                if self._log_console is not None:
                    self._log_console.print(
                        f"Disconnected from devtools ({self.devtools.url})"
                    )
            if self._log_file is not None:
                self._log_file.close()

    async def on_idle(self) -> None:
        """Perform actions when there are no messages in the queue."""
        if self._require_styles_update:
            await self.post_message(messages.StylesUpdated(self))
            self._require_styles_update = False

    def _register_child(self, parent: DOMNode, child: DOMNode) -> bool:
        if child not in self.registry:
            parent.children._append(child)
            self.registry.add(child)
            child.set_parent(parent)
            child.start_messages()
            return True
        return False

    def register(
        self, parent: DOMNode, *anon_widgets: Widget, **widgets: Widget
    ) -> None:
        """Mount widget(s) so they may receive events.

        Args:
            parent (Widget): Parent Widget
        """
        if not anon_widgets and not widgets:
            raise AppError(
                "Nothing to mount, did you forget parent as first positional arg?"
            )
        name_widgets: Iterable[tuple[str | None, Widget]]
        name_widgets = [*((None, widget) for widget in anon_widgets), *widgets.items()]
        apply_stylesheet = self.stylesheet.apply

        for widget_id, widget in name_widgets:
            if widget not in self.registry:
                if widget_id is not None:
                    widget.id = widget_id
                self._register_child(parent, widget)
                if widget.children:
                    self.register(widget, *widget.children)
                apply_stylesheet(widget)

        for _widget_id, widget in name_widgets:
            widget.post_message_no_wait(events.Mount(sender=parent))

    async def _disconnect_devtools(self):
        await self.devtools.disconnect()

    def start_widget(self, parent: Widget, widget: Widget) -> None:
        """Start a widget (run it's task) so that it can receive messages.

        Args:
            parent (Widget): The parent of the Widget.
            widget (Widget): The Widget to start.
        """
        widget.set_parent(parent)
        widget.start_messages()
        widget.post_message_no_wait(events.Mount(sender=parent))

    def is_mounted(self, widget: Widget) -> bool:
        return widget in self.registry

    async def close_all(self) -> None:
        while self.registry:
            child = self.registry.pop()
            await child.close_messages()

    async def remove(self, child: MessagePump) -> None:
        self.registry.remove(child)

    async def shutdown(self):
        await self._disconnect_devtools()
        driver = self._driver
        assert driver is not None
        driver.disable_input()
        await self.close_messages()

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> None:
        if not self._running:
            return
        sync_available = (
            os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal" and not WINDOWS
        )
        if not self._closed:
            console = self.console
            try:
                if sync_available:
                    console.file.write("\x1bP=1s\x1b\\")
                console.print(
                    ScreenRenderable(
                        Control.home(), self.screen._compositor, Control.home()
                    )
                )
                if sync_available:
                    console.file.write("\x1bP=2s\x1b\\")
                console.file.flush()
            except Exception as error:
                self.on_exception(error)

    def refresh_css(self, animate: bool = True) -> None:
        """Refresh CSS.

        Args:
            animate (bool, optional): Also execute CSS animations. Defaults to True.
        """
        stylesheet = self.app.stylesheet
        stylesheet.set_variables(self.get_css_variables())
        stylesheet.reparse()
        stylesheet.update(self.app, animate=animate)
        self.refresh(layout=True)

    def display(self, renderable: RenderableType) -> None:
        if not self._running:
            return
        if not self._closed:
            console = self.console
            try:
                console.print(renderable)
            except Exception as error:
                self.on_exception(error)

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
        return self.screen.get_widget_at(x, y)

    def bell(self) -> None:
        """Play the console 'bell'."""
        self.console.bell()

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
        if isinstance(event, events.Mount):
            screen = Screen()
            self.register(self, screen)
            await self.push_screen(screen)
            await super().on_event(event)

        elif isinstance(event, events.InputEvent) and not event.is_forwarded:
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
                await self.screen.forward_event(event)
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
                raise ActionError("Action namespace {destination} is not known")
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
        """Allow the app an opportunity to dispatch events to action system.

        Args:
            event_name (str): _description_
            event (events.Event): An event object.
            default_namespace (object | None): TODO: _description_

        Returns:
            bool: True if an action was processed.
        """
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
        elif callable(action):
            await action()
        else:
            return False
        return True

    async def handle_update(self, message: messages.Update) -> None:
        message.stop()
        self.app.refresh()

    async def handle_layout(self, message: messages.Layout) -> None:
        message.stop()
        self.app.refresh()

    async def on_key(self, event: events.Key) -> None:
        await self.press(event.key)

    async def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log("shutdown request")
        await self.close_messages()

    async def on_resize(self, event: events.Resize) -> None:
        await self.screen.post_message(event)

    async def action_press(self, key: str) -> None:
        await self.press(key)

    async def action_quit(self) -> None:
        await self.shutdown()

    async def action_bang(self) -> None:
        1 / 0

    async def action_bell(self) -> None:
        self.bell()

    async def action_add_class_(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).add_class(class_name)

    async def action_remove_class_(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).remove_class(class_name)

    async def action_toggle_class(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).toggle_class(class_name)

    async def handle_styles_updated(self, message: messages.StylesUpdated) -> None:
        self.stylesheet.update(self, animate=True)
