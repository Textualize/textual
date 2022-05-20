from __future__ import annotations

import asyncio
from datetime import datetime
import inspect
import io
import os
import platform
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import PurePath
from time import perf_counter
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    TextIO,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

from ._terminal_features import TerminalSupportedFeatures
from ._terminal_modes import Mode
from .events import ModeReport

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover

import rich
import rich.repr
from rich.console import Console, RenderableType
from rich.measure import Measurement
from rich.protocol import is_renderable
from rich.segment import Segments
from rich.style import Style
from rich.traceback import Traceback

from . import actions
from . import events
from . import log
from . import messages
from ._animator import Animator
from ._callback import invoke
from ._context import active_app
from ._event_broker import extract_handler_actions, NoHandler
from .binding import Bindings, NoBinding
from .css.stylesheet import Stylesheet
from .design import ColorSystem
from .devtools.client import DevtoolsClient, DevtoolsConnectionError, DevtoolsLog
from .devtools.redirect_output import StdoutRedirector
from .dom import DOMNode
from .driver import Driver
from .features import parse_features, FeatureFlag
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

# `asyncio.get_event_loop()` is deprecated since Python 3.10:
_ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED = sys.version_info >= (3, 10, 0)

LayoutDefinition = "dict[str, Any]"


DEFAULT_COLORS = ColorSystem(
    primary="#406e8e",
    secondary="#ffa62b",
    warning="#ffa62b",
    error="#ba3c5b",
    success="#6d9f71",
    accent="#ffa62b",
    system="#5a4599",
    dark_surface="#292929",
)

ComposeResult = Iterable[Widget]


class AppError(Exception):
    pass


class ActionError(Exception):
    pass


ReturnType = TypeVar("ReturnType")


@rich.repr.auto
class App(Generic[ReturnType], DOMNode):
    """The base class for Textual Applications"""

    CSS = """

    """

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        log_path: str | PurePath = "",
        log_verbosity: int = 1,
        log_color_system: Literal[
            "auto", "standard", "256", "truecolor", "windows"
        ] = "auto",
        title: str = "Textual Application",
        css_path: str | PurePath | None = None,
        watch_css: bool = False,
    ):
        """Textual application base class

        Args:
            driver_class (Type[Driver] | None, optional): Driver class or ``None`` to auto-detect. Defaults to None.
            log_path (str | PurePath, optional): Path to log file, or "" to disable. Defaults to "".
            log_verbosity (int, optional): Log verbosity from 0-3. Defaults to 1.
            title (str, optional): Default title of the application. Defaults to "Textual Application".
            css_path (str | PurePath | None, optional): Path to CSS or ``None`` for no CSS file. Defaults to None.
            watch_css (bool, optional): Watch CSS for changes. Defaults to False.
        """
        # N.B. This must be done *before* we call the parent constructor, because MessagePump's
        # constructor instantiates a `asyncio.PriorityQueue` and in Python versions older than 3.10
        # this will create some first references to an asyncio loop.
        _init_uvloop()

        self.console = Console(
            file=sys.__stdout__, markup=False, highlight=False, emoji=False
        )
        self.error_console = Console(markup=False, stderr=True)
        self.driver_class = driver_class or self.get_driver_class()
        self._title = title
        self._screen_stack: list[Screen] = []
        self._terminal_features = TerminalSupportedFeatures.from_autodetect()

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
        self._log_file: TextIO | None = None
        if log_path:
            self._log_file = open(log_path, "wt")
            self._log_console = Console(
                file=self._log_file,
                color_system=log_color_system,
                markup=False,
                emoji=False,
                highlight=False,
                width=100,
            )

        self.log_verbosity = log_verbosity

        self.bindings.bind("ctrl+c", "quit", show=False, allow_forward=False)
        self._refresh_required = False

        self.design = DEFAULT_COLORS

        self.stylesheet = Stylesheet(variables=self.get_css_variables())
        self._require_styles_update = False

        self.css_path = css_path

        self.features: frozenset[FeatureFlag] = parse_features(os.getenv("TEXTUAL", ""))

        self.registry: set[MessagePump] = set()
        self.devtools = DevtoolsClient()
        self._return_value: ReturnType | None = None

        self.css_monitor = (
            FileMonitor(css_path, self._on_css_change)
            if ((watch_css or self.debug) and css_path)
            else None
        )

        super().__init__()

    title: Reactive[str] = Reactive("Textual")
    sub_title: Reactive[str] = Reactive("")
    background: Reactive[str] = Reactive("black")
    dark = Reactive(False)

    @property
    def devtools_enabled(self) -> bool:
        """Check if devtools are enabled."""
        return "devtools" in self.features

    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled."""
        return "debug" in self.features

    def exit(self, result: ReturnType | None = None) -> None:
        """Exit the app, and return the supplied result.

        Args:
            result (ReturnType | None, optional): Return value. Defaults to None.
        """
        self._return_value = result
        self.close_messages_no_wait()

    @property
    def focus_chain(self) -> list[Widget]:
        """Get widgets that may receive focus, in focus order."""
        widgets: list[Widget] = []
        add_widget = widgets.append
        root = self.screen
        stack: list[Iterator[Widget]] = [iter(root.focusable_children)]
        pop = stack.pop
        push = stack.append

        while stack:
            node = next(stack[-1], None)
            if node is None:
                pop()
            else:
                if node.is_container and node.can_focus_children:
                    push(iter(node.focusable_children))
                else:
                    if node.can_focus:
                        add_widget(node)

        return widgets

    def _set_active(self) -> None:
        """Set this app to be the currently active app."""
        active_app.set(self)

    def _move_focus(self, direction: int = 0) -> Widget | None:
        """Move the focus in the given direction.

        Args:
            direction (int, optional): 1 to move forward, -1 to move backward, or
                0 to highlight the current focus.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        focusable_widgets = self.focus_chain

        if not focusable_widgets:
            # Nothing focusable, so nothing to do
            return self.focused
        if self.focused is None:
            # Nothing currently focused, so focus the first one
            self.set_focus(focusable_widgets[0])
        else:
            try:
                # Find the index of the currently focused widget
                current_index = focusable_widgets.index(self.focused)
            except ValueError:
                # Focused widget was removed in the interim, start again
                self.set_focus(focusable_widgets[0])
            else:
                # Only move the focus if we are currently showing the focus
                if direction:
                    current_index = (current_index + direction) % len(focusable_widgets)
                    self.set_focus(focusable_widgets[current_index])

        return self.focused

    def show_focus(self) -> Widget | None:
        """Highlight the currently focused widget.

        Returns:
            Widget | None: Focused widget, or None for no focus.
        """
        return self._move_focus(0)

    def focus_next(self) -> Widget | None:
        """Focus the next widget.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        return self._move_focus(1)

    def focus_previous(self) -> Widget | None:
        """Focus the previous widget.

        Returns:
            Widget | None: Newly focused widget, or None for no focus.
        """
        return self._move_focus(-1)

    def compose(self) -> ComposeResult:
        """Yield child widgets for a container."""
        return
        yield

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
                        f"{key}={value!r}" for key, value in kwargs.items()
                    )
                    output = f"{output} {key_values}" if output else key_values
                if self._log_console is not None:
                    self._log_console.print(output, soft_wrap=True)
                if self.devtools.is_connected:
                    self.devtools.log(
                        DevtoolsLog(output, caller=_textual_calling_frame)
                    )
        except Exception as error:
            self.on_exception(error)

    def action_screenshot(self, path: str | None = None) -> None:
        """Action to save a screenshot."""
        self.save_screenshot(path)

    def export_screenshot(self) -> str:
        """Export a SVG screenshot of the current screen.

        Args:
            path (str | None, optional): Path of the SVG to save, or None to
                generate a path automatically. Defaults to None.
        """

        console = Console(
            width=self.console.width,
            height=self.console.height,
            file=io.StringIO(),
            force_terminal=True,
            color_system="truecolor",
            record=True,
        )
        console.print(self.screen._compositor)
        return console.export_svg(title=self.title)

    def save_screenshot(self, path: str | None = None) -> str:
        """Save a screenshot of the current screen.

        Args:
            path (str | None, optional): Path to SVG to save or None to pick
                a filename automatically. Defaults to None.

        Returns:
            str: Filename of screenshot.
        """
        if path is None:
            svg_path = f"{self.title.lower()}_{datetime.now().isoformat()}.svg"
            svg_path = svg_path.replace("/", "_").replace("\\", "_")
        else:
            svg_path = path
        screenshot_svg = self.export_screenshot()
        with open(svg_path, "w") as svg_file:
            svg_file.write(screenshot_svg)
        return svg_path

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

    def run(self) -> ReturnType | None:
        """The entry point to run a Textual app."""

        async def run_app() -> None:
            await self.process_messages()

        if _ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED:
            # N.B. This doesn't work with Python<3.10, as we end up with 2 event loops:
            asyncio.run(run_app())
        else:
            # However, this works with Python<3.10:
            event_loop = asyncio.get_event_loop()
            event_loop.run_until_complete(run_app())

        return self._return_value

    async def _on_css_change(self) -> None:
        """Called when the CSS changes (if watch_css is True)."""
        if self.css_path is not None:

            try:
                time = perf_counter()
                stylesheet = self.stylesheet.copy()
                stylesheet.read(self.css_path)
                stylesheet.parse()
                elapsed = (perf_counter() - time) * 1000
                self.log(f"<stylesheet> loaded {self.css_path!r} in {elapsed:.0f} ms")
            except Exception as error:
                # TODO: Catch specific exceptions
                self.bell()
                self.log(error)
            else:
                self.stylesheet = stylesheet
                self.reset_styles()
                self.stylesheet.update(self)
                self.screen.refresh(layout=True)

    def render(self, styles: Style) -> RenderableType:
        return ""

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

        Raises:
            NoMatchingNodesError: if no children could be found for this ID
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

    def push_screen(self, screen: Screen | None = None) -> Screen:
        """Push a new screen on the screen stack.

        Args:
            screen (Screen | None, optional): A new Screen instance or None to create
                one internally. Defaults to None.

        Returns:
            Screen: Newly active screen.
        """
        new_screen = Screen() if screen is None else screen
        self._screen_stack.append(new_screen)
        return new_screen

    def set_focus(self, widget: Widget | None) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget (Widget): [description]
        """
        self.log("set_focus", widget=widget)
        if widget == self.focused:
            # Widget is already focused
            return

        if widget is None:
            # No focus, so blur currently focused widget if it exists
            if self.focused is not None:
                self.focused.post_message_no_wait(events.Blur(self))
                self.focused.emit_no_wait(events.DescendantBlur(self))
                self.focused = None
        elif widget.can_focus:
            if self.focused != widget:
                if self.focused is not None:
                    # Blur currently focused widget
                    self.focused.post_message_no_wait(events.Blur(self))
                    self.focused.emit_no_wait(events.DescendantBlur(self))
                # Change focus
                self.focused = widget
                # Send focus event
                widget.post_message_no_wait(events.Focus(self))
                widget.emit_no_wait(events.DescendantFocus(self))

    async def _set_mouse_over(self, widget: Widget | None) -> None:
        """Called when the mouse is over another widget.

        Args:
            widget (Widget | None): Widget under mouse, or None for no widgets.
        """
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

        assert all(
            is_renderable(renderable) for renderable in renderables
        ), "Can only call panic with strings or Rich renderables"

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
        self.bell()
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
        self._set_active()

        if self.devtools_enabled:
            try:
                await self.devtools.connect()
                self.log(f"Connected to devtools ({self.devtools.url})")
            except DevtoolsConnectionError:
                self.log(f"Couldn't connect to devtools ({self.devtools.url})")

        self.log("---")
        self.log(driver=self.driver_class)
        self.log(loop=asyncio.get_running_loop())
        self.log(terminal_features=self._terminal_features)
        self.log(features=self.features)

        try:
            if self.css_path is not None:
                self.stylesheet.read(self.css_path)
            if self.CSS is not None:
                self.stylesheet.add_source(
                    self.CSS, path=f"<{self.__class__.__name__}>"
                )
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

            driver = self._driver = self.driver_class(self.console, self)
            driver.start_application_mode()
            try:
                mount_event = events.Mount(sender=self)
                await self.dispatch_message(mount_event)

                # TODO: don't override `self.console` here
                self.console = Console(file=sys.__stdout__)
                self.title = self._title
                self.refresh()
                await self.animator.start()

                with redirect_stdout(StdoutRedirector(self.devtools, self._log_file)):  # type: ignore
                    await super().process_messages()
                    await self.animator.stop()
                    await self.close_all()
            finally:
                driver.stop_application_mode()
        except Exception as error:
            self.on_exception(error)
        finally:
            self._running = False
            self._print_error_renderables()
            if self.devtools.is_connected:
                await self._disconnect_devtools()
                if self._log_console is not None:
                    self._log_console.print(
                        f"Disconnected from devtools ({self.devtools.url})"
                    )
            if self._log_file is not None:
                self._log_file.close()
                self._log_console = None

    def on_mount(self) -> None:
        widgets = list(self.compose())
        if widgets:
            self.mount(*widgets)

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
            child.on_register(self)
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
        self._display(self.screen._compositor)

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

    def _display(self, renderable: RenderableType) -> None:
        """Display a renderable within a sync.

        Args:
            renderable (RenderableType): A Rich renderable.
        """
        if self._running and not self._closed:
            console = self.console
            (
                sync_update_start,
                sync_update_end,
            ) = self._terminal_features.synchronized_update_sequences()
            if sync_update_start:
                console.file.write(sync_update_start)
            try:
                console.print(renderable)
            except Exception as error:
                self.on_exception(error)
            if sync_update_end:
                console.file.write(sync_update_end)
            console.file.flush()

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
            self.push_screen(screen)
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

        elif isinstance(event, ModeReport):
            if event.mode is Mode.SynchronizedOutput:
                is_supported = event.mode_is_supported
                log(
                    f"SynchronizedOutput (aka 'mode2026') {'is' if is_supported else ' is not'} supported"
                )
                self._terminal_features.mode2026_synchronized_update = is_supported

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

        log("<action>", action)
        await self.dispatch_action(action_target, action_name, params)

    async def dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> None:
        log(
            "<action>",
            namespace=namespace,
            action_name=action_name,
            params=params,
        )
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
        if event.key == "tab":
            self.focus_next()
        elif event.key == "shift+tab":
            self.focus_previous()
        else:
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


_uvloop_init_done: bool = False


def _init_uvloop() -> None:
    """
    Import and install the `uvloop` asyncio policy, if available.
    This is done only once, even if the function is called multiple times.
    """
    global _uvloop_init_done

    if _uvloop_init_done:
        return

    try:
        import uvloop
    except ImportError:
        pass
    else:
        uvloop.install()

    _uvloop_init_done = True
