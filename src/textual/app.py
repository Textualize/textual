from __future__ import annotations

import asyncio
import inspect
import io
import os
import platform
import sys
import warnings
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path, PurePath
from time import perf_counter
from typing import Any, Generic, Iterable, Iterator, Type, TypeVar, cast
from weakref import WeakSet, WeakValueDictionary

from ._ansi_sequences import SYNC_END, SYNC_START
from ._path import _make_path_object_relative

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover

import nanoid
import rich
import rich.repr
from rich.console import Console, RenderableType
from rich.protocol import is_renderable
from rich.segment import Segment, Segments
from rich.traceback import Traceback

from . import Logger, LogGroup, LogVerbosity, actions, events, log, messages
from ._animator import Animator
from ._callback import invoke
from ._context import active_app
from ._event_broker import NoHandler, extract_handler_actions
from .binding import Bindings, NoBinding
from .css.query import NoMatchingNodesError
from .css.stylesheet import Stylesheet
from .design import ColorSystem
from .devtools.client import DevtoolsClient, DevtoolsConnectionError, DevtoolsLog
from .devtools.redirect_output import StdoutRedirector
from .dom import DOMNode
from .driver import Driver
from .drivers.headless_driver import HeadlessDriver
from .features import FeatureFlag, parse_features
from .file_monitor import FileMonitor
from .geometry import Offset, Region, Size
from .messages import CallbackType
from .reactive import Reactive
from .renderables.blank import Blank
from .screen import Screen
from .widget import Widget

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"

# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)

# `asyncio.get_event_loop()` is deprecated since Python 3.10:
_ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED = sys.version_info >= (3, 10, 0)

LayoutDefinition = "dict[str, Any]"


DEFAULT_COLORS = {
    "dark": ColorSystem(
        primary="#004578",
        secondary="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        accent="#0178D4",
        dark=True,
    ),
    "light": ColorSystem(
        primary="#004578",
        secondary="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        accent="#0178D4",
        dark=False,
    ),
}


ComposeResult = Iterable[Widget]
RenderResult = RenderableType


class AppError(Exception):
    pass


class ActionError(Exception):
    pass


class ScreenError(Exception):
    pass


class ScreenStackError(ScreenError):
    """Raised when attempting to pop the last screen from the stack."""


ReturnType = TypeVar("ReturnType")


class _NullFile:
    def write(self, text: str) -> None:
        pass

    def flush(self) -> None:
        pass


@rich.repr.auto
class App(Generic[ReturnType], DOMNode):
    """The base class for Textual Applications.

    Args:
        driver_class (Type[Driver] | None, optional): Driver class or ``None`` to auto-detect. Defaults to None.
        title (str | None, optional): Title of the application. If ``None``, the title is set to the name of the ``App`` subclass. Defaults to ``None``.
        css_path (str | PurePath | None, optional): Path to CSS or ``None`` for no CSS file. Defaults to None.
        watch_css (bool, optional): Watch CSS for changes. Defaults to False.

    """

    # Inline CSS for quick scripts (generally css_path should be preferred.)
    CSS = ""

    # Default (lowest priority) CSS
    DEFAULT_CSS = """
    App {
        background: $background;
        color: $text;
    }
    """

    SCREENS: dict[str, Screen] = {}

    _BASE_PATH: str | None = None
    CSS_PATH: str | None = None

    focused: Reactive[Widget | None] = Reactive(None)

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        title: str | None = None,
        css_path: str | PurePath | None = None,
        watch_css: bool = False,
    ):
        # N.B. This must be done *before* we call the parent constructor, because MessagePump's
        # constructor instantiates a `asyncio.PriorityQueue` and in Python versions older than 3.10
        # this will create some first references to an asyncio loop.
        _init_uvloop()

        super().__init__()
        self.features: frozenset[FeatureFlag] = parse_features(os.getenv("TEXTUAL", ""))

        self.console = Console(
            file=(_NullFile() if self.is_headless else sys.__stdout__),
            markup=False,
            highlight=False,
            emoji=False,
            legacy_windows=False,
        )
        self.error_console = Console(markup=False, stderr=True)
        self.driver_class = driver_class or self.get_driver_class()
        self._title = title
        self._screen_stack: list[Screen] = []
        self._sync_available = False

        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._action_targets = {"app", "screen"}
        self._animator = Animator(self)
        self.animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)
        if title is None:
            self._title = f"{self.__class__.__name__}"
        else:
            self._title = title

        self._logger = Logger(self._log)

        self._bindings.bind("ctrl+c", "quit", show=False, allow_forward=False)
        self._refresh_required = False

        self.design = DEFAULT_COLORS

        self.stylesheet = Stylesheet(variables=self.get_css_variables())
        self._require_stylesheet_update: set[DOMNode] = set()

        # We want the CSS path to be resolved from the location of the App subclass
        css_path = css_path or self.CSS_PATH
        if css_path is not None:
            if isinstance(css_path, str):
                css_path = Path(css_path)
            css_path = _make_path_object_relative(css_path, self) if css_path else None

        self.css_path = css_path

        self._registry: WeakSet[DOMNode] = WeakSet()

        self._installed_screens: WeakValueDictionary[
            str, Screen
        ] = WeakValueDictionary()
        self._installed_screens.update(**self.SCREENS)

        self.devtools = DevtoolsClient()
        self._return_value: ReturnType | None = None

        self.css_monitor = (
            FileMonitor(self.css_path, self._on_css_change)
            if ((watch_css or self.debug) and self.css_path)
            else None
        )
        self._screenshot: str | None = None

    title: Reactive[str] = Reactive("Textual")
    sub_title: Reactive[str] = Reactive("")
    dark: Reactive[bool] = Reactive(True)

    @property
    def devtools_enabled(self) -> bool:
        """Check if devtools are enabled.

        Returns:
            bool: True if devtools are enabled.

        """
        return "devtools" in self.features

    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled.

        Returns:
            bool: True if debug mode is enabled.

        """
        return "debug" in self.features

    @property
    def is_headless(self) -> bool:
        """Check if the app is running in 'headless' mode.

        Returns:
            bool: True if the app is in headless mode.

        """
        return "headless" in self.features

    @property
    def screen_stack(self) -> list[Screen]:
        """Get a *copy* of the screen stack.

        Returns:
            list[Screen]: List of screens.

        """
        return self._screen_stack.copy()

    def exit(self, result: ReturnType | None = None) -> None:
        """Exit the app, and return the supplied result.

        Args:
            result (ReturnType | None, optional): Return value. Defaults to None.
        """
        self._return_value = result
        self._close_messages_no_wait()

    @property
    def focus_chain(self) -> list[Widget]:
        """Get widgets that may receive focus, in focus order.

        Returns:
            list[Widget]: List of Widgets in focus order.

        """
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

    @property
    def bindings(self) -> Bindings:
        """Get current bindings."""
        if self.focused is None:
            return self._bindings
        else:
            return Bindings.merge(
                node._bindings for node in reversed(self.focused.ancestors)
            )

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
        variables = self.design["dark" if self.dark else "light"].generate()
        return variables

    def watch_dark(self, dark: bool) -> None:
        """Watches the dark bool."""

        self.screen.dark = dark
        if dark:
            self.add_class("-dark-mode")
            self.remove_class("-light-mode")
        else:
            self.remove_class("-dark-mode")
            self.add_class("-light-mode")

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
        yield "id", self.id, None
        if self.name:
            yield "name", self.name
        if self.classes:
            yield "classes", set(self.classes)
        pseudo_classes = self.pseudo_classes
        if pseudo_classes:
            yield "pseudo_classes", set(pseudo_classes)

    @property
    def is_transparent(self) -> bool:
        return True

    @property
    def animator(self) -> Animator:
        return self._animator

    @property
    def screen(self) -> Screen:
        """Get the current screen.

        Raises:
            ScreenStackError: If there are no screens on the stack.

        Returns:
            Screen: The currently active screen.
        """
        try:
            return self._screen_stack[-1]
        except IndexError:
            raise ScreenStackError("No screens on stack") from None

    @property
    def size(self) -> Size:
        """Get the size of the terminal.

        Returns:
            Size: Size of the terminal
        """
        return Size(*self.console.size)

    @property
    def log(self) -> Logger:
        return self._logger

    def _log(
        self,
        group: LogGroup,
        verbosity: LogVerbosity,
        *objects: Any,
        _textual_calling_frame: inspect.FrameInfo | None = None,
        **kwargs,
    ) -> None:
        """Write to logs or devtools.

        Positional args will logged. Keyword args will be prefixed with the key.

        Example:
            ```python
            data = [1,2,3]
            self.log("Hello, World", state=data)
            self.log(self.tree)
            self.log(locals())
            ```

        Args:
            verbosity (int, optional): Verbosity level 0-3. Defaults to 1.
        """

        if not self.devtools.is_connected:
            return

        if verbosity.value > LogVerbosity.NORMAL.value and not self.devtools.verbose:
            return

        if not _textual_calling_frame:
            _textual_calling_frame = inspect.stack()[1]

        try:
            if len(objects) == 1 and not kwargs:
                self.devtools.log(
                    DevtoolsLog(objects, caller=_textual_calling_frame),
                    group,
                    verbosity,
                )
            else:
                output = " ".join(str(arg) for arg in objects)
                if kwargs:
                    key_values = " ".join(
                        f"{key}={value!r}" for key, value in kwargs.items()
                    )
                    output = f"{output} {key_values}" if output else key_values
                self.devtools.log(
                    DevtoolsLog(output, caller=_textual_calling_frame),
                    group,
                    verbosity,
                )
        except Exception as error:
            self._handle_exception(error)

    def action_toggle_dark(self) -> None:
        """Action to toggle dark mode."""
        self.dark = not self.dark

    def action_screenshot(self, filename: str | None, path: str = "~/") -> None:
        """Save an SVG "screenshot". This action will save a SVG file containing the current contents of the screen.

        Args:
            filename (str | None, optional): Filename of screenshot, or None to auto-generate. Defaults to None.
            path (str, optional): Path to directory. Defaults to "~/".
        """
        self.save_screenshot(filename, path)

    def export_screenshot(self, *, title: str | None = None) -> str:
        """Export a SVG screenshot of the current screen.

        Args:
            title (str | None, optional): The title of the exported screenshot or None
                to use app title. Defaults to None.

        """

        console = Console(
            width=self.console.width,
            height=self.console.height,
            file=io.StringIO(),
            force_terminal=True,
            color_system="truecolor",
            record=True,
            legacy_windows=False,
        )
        screen_render = self.screen._compositor.render(full=True)
        console.print(screen_render)
        return console.export_svg(title=title or self.title)

    def save_screenshot(
        self,
        filename: str | None = None,
        path: str = "./",
        time_format: str = "%Y-%m-%d %X %f",
    ) -> str:
        """Save a SVG screenshot of the current screen.

        Args:
            filename (str | None, optional): Filename of SVG screenshot, or None to auto-generate
                a filename with the date and time. Defaults to None.
            path (str, optional): Path to directory for output. Defaults to current working directory.
            time_format (str, optional): Time format to use if filename is None. Defaults to "%Y-%m-%d %X %f".

        Returns:
            str: Filename of screenshot.
        """
        if filename is None:
            svg_filename = (
                f"{self.title.lower()} {datetime.now().strftime(time_format)}.svg"
            )
            svg_filename = svg_filename.replace("/", "_").replace("\\", "_")
        else:
            svg_filename = filename
        svg_path = os.path.expanduser(os.path.join(path, svg_filename))
        screenshot_svg = self.export_screenshot()
        with open(svg_path, "w") as svg_file:
            svg_file.write(screenshot_svg)
        return svg_path

    def bind(
        self,
        keys: str,
        action: str,
        *,
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
        self._bindings.bind(
            keys, action, description, show=show, key_display=key_display
        )

    def run(
        self,
        *,
        quit_after: float | None = None,
        headless: bool = False,
        press: Iterable[str] | None = None,
        screenshot: bool = False,
        screenshot_title: str | None = None,
    ) -> ReturnType | None:
        """The main entry point for apps.

        Args:
            quit_after (float | None, optional): Quit after a given number of seconds, or None
                to run forever. Defaults to None.
            headless (bool, optional): Run in "headless" mode (don't write to stdout).
            press (str, optional): An iterable of keys to simulate being pressed.
            screenshot (bool, optional): Take a screenshot after pressing keys (svg data stored in self._screenshot). Defaults to False.
            screenshot_title (str | None, optional): Title of screenshot, or None to use App title. Defaults to None.

        Returns:
            ReturnType | None: The return value specified in `App.exit` or None if exit wasn't called.
        """

        if headless:
            self.features = cast(
                "frozenset[FeatureFlag]", self.features.union({"headless"})
            )

        async def run_app() -> None:
            if quit_after is not None:
                self.set_timer(quit_after, self.shutdown)
            if press is not None:
                app = self

                async def press_keys() -> None:
                    """A task to send key events."""
                    assert press
                    driver = app._driver
                    assert driver is not None
                    await asyncio.sleep(0.01)
                    for key in press:
                        if key == "_":
                            print("(pause)")
                            await asyncio.sleep(0.05)
                        else:
                            print(f"press {key!r}")
                            driver.send_event(
                                events.Key(self, key, key if len(key) == 1 else None)
                            )
                            await asyncio.sleep(0.01)

                    await app._animator.wait_for_idle()

                    if screenshot:
                        self._screenshot = self.export_screenshot(
                            title=screenshot_title
                        )
                    await self.shutdown()

                async def press_keys_task():
                    """Press some keys in the background."""
                    asyncio.create_task(press_keys())

                await self._process_messages(ready_callback=press_keys_task)
            else:
                await self._process_messages()

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
                self.log.system(
                    f"<stylesheet> loaded {self.css_path!r} in {elapsed:.0f} ms"
                )
            except Exception as error:
                # TODO: Catch specific exceptions
                self.log.error(error)
                self.bell()
            else:
                self.stylesheet = stylesheet
                self.reset_styles()
                self.stylesheet.update(self)
                self.screen.refresh(layout=True)

    def render(self) -> RenderableType:
        return Blank(self.styles.background)

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

    def update_styles(self, node: DOMNode | None = None) -> None:
        """Request update of styles.

        Should be called whenever CSS classes / pseudo classes change.

        """
        self._require_stylesheet_update.add(self.screen if node is None else node)
        self.check_idle()

    def update_visible_styles(self) -> None:
        """Update visible styles only."""
        self._require_stylesheet_update.update(self.screen.visible_widgets)
        self.check_idle()

    def mount(self, *anon_widgets: Widget, **widgets: Widget) -> None:
        """Mount widgets. Widgets specified as positional args, or keywords args. If supplied
        as keyword args they will be assigned an id of the key.

        """
        self._register(self.screen, *anon_widgets, **widgets)

    def mount_all(self, widgets: Iterable[Widget]) -> None:
        """Mount widgets from an iterable.

        Args:
            widgets (Iterable[Widget]): An iterable of widgets.
        """
        for widget in widgets:
            self._register(self.screen, widget)

    def is_screen_installed(self, screen: Screen | str) -> bool:
        """Check if a given screen has been installed.

        Args:
            screen (Screen | str): Either a Screen object or screen name (the `name` argument when installed).

        Returns:
            bool: True if the screen is currently installed,
        """
        if isinstance(screen, str):
            return screen in self._installed_screens
        else:
            return screen in self._installed_screens.values()

    def get_screen(self, screen: Screen | str) -> Screen:
        """Get an installed screen.

        If the screen isn't running, it will be registered before it is run.

        Args:
            screen (Screen | str): Either a Screen object or screen name (the `name` argument when installed).

        Raises:
            KeyError: If the named screen doesn't exist.

        Returns:
            Screen: A screen instance.
        """
        if isinstance(screen, str):
            try:
                next_screen = self._installed_screens[screen]
            except KeyError:
                raise KeyError(f"No screen called {screen!r} installed") from None
        else:
            next_screen = screen
        if not next_screen.is_running:
            self._register(self, next_screen)
        return next_screen

    def _replace_screen(self, screen: Screen) -> Screen:
        """Handle the replaced screen.

        Args:
            screen (Screen): A screen object.

        Returns:
            Screen: The screen that was replaced.

        """
        screen.post_message_no_wait(events.ScreenSuspend(self))
        self.log.system(f"{screen} SUSPENDED")
        if not self.is_screen_installed(screen) and screen not in self._screen_stack:
            screen.remove()
            self.log.system(f"{screen} REMOVED")
        return screen

    def push_screen(self, screen: Screen | str) -> None:
        """Push a new screen on the screen stack.

        Args:
            screen (Screen | str): A Screen instance or the name of an installed screen.

        """
        next_screen = self.get_screen(screen)
        self._screen_stack.append(next_screen)
        self.screen.post_message_no_wait(events.ScreenResume(self))
        self.log.system(f"{self.screen} is current (PUSHED)")

    def switch_screen(self, screen: Screen | str) -> None:
        """Switch to a another screen by replacing the top of the screen stack with a new screen.

        Args:
            screen (Screen | str): Either a Screen object or screen name (the `name` argument when installed).

        """
        if self.screen is not screen:
            self._replace_screen(self._screen_stack.pop())
            next_screen = self.get_screen(screen)
            self._screen_stack.append(next_screen)
            self.screen.post_message_no_wait(events.ScreenResume(self))
            self.log.system(f"{self.screen} is current (SWITCHED)")

    def install_screen(self, screen: Screen, name: str | None = None) -> str:
        """Install a screen.

        Args:
            screen (Screen): Screen to install.
            name (str | None, optional): Unique name of screen or None to auto-generate.
                Defaults to None.

        Raises:
            ScreenError: If the screen can't be installed.

        Returns:
            str: The name of the screen
        """
        if name is None:
            name = nanoid.generate()
        if name in self._installed_screens:
            raise ScreenError(f"Can't install screen; {name!r} is already installed")
        if screen in self._installed_screens.values():
            raise ScreenError(
                "Can't install screen; {screen!r} has already been installed"
            )
        self._installed_screens[name] = screen
        self.get_screen(name)  # Ensures screen is running
        self.log.system(f"{screen} INSTALLED name={name!r}")
        return name

    def uninstall_screen(self, screen: Screen | str) -> str | None:
        """Uninstall a screen. If the screen was not previously installed then this
        method is a null-op.

        Args:
            screen (Screen | str): The screen to uninstall or the name of a installed screen.

        Returns:
            str | None: The name of the screen that was uninstalled, or None if no screen was uninstalled.
        """
        if isinstance(screen, str):
            if screen not in self._installed_screens:
                return None
            uninstall_screen = self._installed_screens[screen]
            if uninstall_screen in self._screen_stack:
                raise ScreenStackError("Can't uninstall screen in screen stack")
            del self._installed_screens[screen]
            self.log.system(f"{uninstall_screen} UNINSTALLED name={screen!r}")
            return screen
        else:
            if screen in self._screen_stack:
                raise ScreenStackError("Can't uninstall screen in screen stack")
            for name, installed_screen in self._installed_screens.items():
                if installed_screen is screen:
                    self._installed_screens.pop(name)
                    self.log.system(f"{screen} UNINSTALLED name={name!r}")
                    return name
        return None

    def pop_screen(self) -> Screen:
        """Pop the current screen from the stack, and switch to the previous screen.

        Returns:
            Screen: The screen that was replaced.
        """
        screen_stack = self._screen_stack
        if len(screen_stack) <= 1:
            raise ScreenStackError(
                "Can't pop screen; there must be at least one screen on the stack"
            )
        previous_screen = self._replace_screen(screen_stack.pop())
        self.screen._screen_resized(self.size)
        self.screen.post_message_no_wait(events.ScreenResume(self))
        self.log.system(f"{self.screen} is active")
        return previous_screen

    def set_focus(self, widget: Widget | None, scroll_visible: bool = True) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget (Widget): Widget to focus.
            scroll_visible (bool, optional): Scroll widget in to view.
        """
        if widget is self.focused:
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
                if scroll_visible:
                    self.screen.scroll_to_widget(widget)
                widget.post_message_no_wait(events.Focus(self))
                widget.emit_no_wait(events.DescendantFocus(self))

    def _reset_focus(self, widget: Widget) -> None:
        """Reset the focus when a widget is removed

        Args:
            widget (Widget): A widget that is removed.
        """
        for sibling in widget.siblings:
            if sibling.can_focus:
                sibling.focus()
                break
        else:
            self.focused = None

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
            if self.mouse_over is not widget:
                try:
                    if self.mouse_over is not None:
                        await self.mouse_over._forward_event(events.Leave(self))
                    if widget is not None:
                        await widget._forward_event(events.Enter(self))
                finally:
                    self.mouse_over = widget

    def capture_mouse(self, widget: Widget | None) -> None:
        """Send all mouse events to the given widget, disable mouse capture.

        Args:
            widget (Widget | None): If a widget, capture mouse event, or None to end mouse capture.
        """
        if widget == self.mouse_captured:
            return
        if self.mouse_captured is not None:
            self.mouse_captured.post_message_no_wait(
                events.MouseRelease(self, self.mouse_position)
            )
        self.mouse_captured = widget
        if widget is not None:
            widget.post_message_no_wait(events.MouseCapture(self, self.mouse_position))

    def panic(self, *renderables: RenderableType) -> None:
        """Exits the app then displays a message.

        Args:
            *renderables (RenderableType, optional): Rich renderables to display on exit.
        """

        assert all(
            is_renderable(renderable) for renderable in renderables
        ), "Can only call panic with strings or Rich renderables"

        def render(renderable: RenderableType) -> list[Segment]:
            """Render a panic renderables."""
            segments = list(self.console.render(renderable, self.console.options))
            return segments

        pre_rendered = [Segments(render(renderable)) for renderable in renderables]
        self._exit_renderables.extend(pre_rendered)
        self._close_messages_no_wait()

    def _handle_exception(self, error: Exception) -> None:
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
        self._close_messages_no_wait()

    def _print_error_renderables(self) -> None:
        for renderable in self._exit_renderables:
            self.error_console.print(renderable)
        self._exit_renderables.clear()

    async def _process_messages(
        self, ready_callback: CallbackType | None = None
    ) -> None:
        self._set_active()

        if self.devtools_enabled:
            try:
                await self.devtools.connect()
                self.log.system(f"Connected to devtools ( {self.devtools.url} )")
            except DevtoolsConnectionError:
                self.log.system(f"Couldn't connect to devtools ( {self.devtools.url} )")

        self.log.system("---")

        self.log.system(driver=self.driver_class)
        self.log.system(loop=asyncio.get_running_loop())
        self.log.system(features=self.features)

        try:
            if self.css_path is not None:
                self.stylesheet.read(self.css_path)
            for path, css, tie_breaker in self.get_default_css():
                self.stylesheet.add_source(
                    css, path=path, is_default_css=True, tie_breaker=tie_breaker
                )
            if self.CSS:
                try:
                    app_css_path = (
                        f"{inspect.getfile(self.__class__)}:{self.__class__.__name__}"
                    )
                except TypeError:
                    app_css_path = f"{self.__class__.__name__}"
                self.stylesheet.add_source(
                    self.CSS, path=app_css_path, is_default_css=False
                )
        except Exception as error:
            self._handle_exception(error)
            self._print_error_renderables()
            return

        if self.css_monitor:
            self.set_interval(0.25, self.css_monitor, name="css monitor")
            self.log.system("[b green]STARTED[/]", self.css_monitor)

        process_messages = super()._process_messages

        async def run_process_messages():
            compose_event = events.Compose(sender=self)
            await self._dispatch_message(compose_event)
            mount_event = events.Mount(sender=self)
            await self._dispatch_message(mount_event)

            self.title = self._title
            self.stylesheet.update(self)
            self.refresh()
            await self.animator.start()
            await self._ready()
            if ready_callback is not None:
                await ready_callback()
            await process_messages()
            await self.animator.stop()
            await self._close_all()

        self._running = True
        try:
            load_event = events.Load(sender=self)
            await self._dispatch_message(load_event)

            driver: Driver
            driver_class = cast(
                "type[Driver]",
                HeadlessDriver if self.is_headless else self.driver_class,
            )
            driver = self._driver = driver_class(self.console, self)

            driver.start_application_mode()
            try:
                if self.is_headless:
                    await run_process_messages()
                else:
                    redirector = StdoutRedirector(self.devtools)
                    with redirect_stderr(redirector):
                        with redirect_stdout(redirector):  # type: ignore
                            await run_process_messages()
            finally:
                driver.stop_application_mode()
        except Exception as error:
            self._handle_exception(error)
        finally:
            self._running = False
            self._print_error_renderables()
            if self.devtools.is_connected:
                await self._disconnect_devtools()

    async def _ready(self) -> None:
        """Called immediately prior to processing messages.

        May be used as a hook for any operations that should run first.

        """
        try:
            screenshot_timer = float(os.environ.get("TEXTUAL_SCREENSHOT", "0"))
        except ValueError:
            return

        screenshot_title = os.environ.get("TEXTUAL_SCREENSHOT_TITLE")

        if not screenshot_timer:
            return

        async def on_screenshot():
            """Used by docs plugin."""
            svg = self.export_screenshot(title=screenshot_title)
            self._screenshot = svg  # type: ignore
            await self.shutdown()

        self.set_timer(screenshot_timer, on_screenshot, name="screenshot timer")

    def _on_compose(self) -> None:
        widgets = self.compose()
        self.mount_all(widgets)

    def _on_idle(self) -> None:
        """Perform actions when there are no messages in the queue."""
        if self._require_stylesheet_update:
            nodes: set[DOMNode] = {
                child
                for node in self._require_stylesheet_update
                for child in node.walk_children()
            }
            self._require_stylesheet_update.clear()
            self.stylesheet.update_nodes(nodes, animate=True)

    def _register_child(self, parent: DOMNode, child: Widget) -> bool:
        if child not in self._registry:
            parent.children._append(child)
            self._registry.add(child)
            child._attach(parent)
            child._post_register(self)
            child._start_messages()
            return True
        return False

    def _register(
        self, parent: DOMNode, *anon_widgets: Widget, **widgets: Widget
    ) -> None:
        """Mount widget(s) so they may receive events.

        Args:
            parent (Widget): Parent Widget
        """
        if not anon_widgets and not widgets:
            return
        name_widgets: Iterable[tuple[str | None, Widget]]
        name_widgets = [*((None, widget) for widget in anon_widgets), *widgets.items()]
        apply_stylesheet = self.stylesheet.apply

        for widget_id, widget in name_widgets:
            if not isinstance(widget, Widget):
                raise AppError(f"Can't register {widget!r}; expected a Widget instance")
            if widget not in self._registry:
                if widget_id is not None:
                    widget.id = widget_id
                self._register_child(parent, widget)
                if widget.children:
                    self._register(widget, *widget.children)
                apply_stylesheet(widget)

        for _widget_id, widget in name_widgets:
            widget.post_message_no_wait(events.Mount(sender=parent))

    def _unregister(self, widget: Widget) -> None:
        """Unregister a widget.

        Args:
            widget (Widget): A Widget to unregister
        """
        self._reset_focus(widget)

        if isinstance(widget._parent, Widget):
            widget._parent.children._remove(widget)
            widget._detach()
        self._registry.discard(widget)

    async def _disconnect_devtools(self):
        await self.devtools.disconnect()

    def _start_widget(self, parent: Widget, widget: Widget) -> None:
        """Start a widget (run it's task) so that it can receive messages.

        Args:
            parent (Widget): The parent of the Widget.
            widget (Widget): The Widget to start.
        """
        widget._attach(parent)
        widget._start_messages()
        widget.post_message_no_wait(events.Mount(sender=parent))

    def is_mounted(self, widget: Widget) -> bool:
        return widget in self._registry

    async def _close_all(self) -> None:
        while self._registry:
            child = self._registry.pop()
            await child._close_messages()

    async def shutdown(self):
        await self._disconnect_devtools()
        driver = self._driver
        if driver is not None:
            driver.disable_input()
        await self._close_messages()

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> None:
        self.screen.refresh(repaint=repaint, layout=layout)
        self.check_idle()

    def refresh_css(self, animate: bool = True) -> None:
        """Refresh CSS.

        Args:
            animate (bool, optional): Also execute CSS animations. Defaults to True.
        """
        stylesheet = self.app.stylesheet
        stylesheet.set_variables(self.get_css_variables())
        stylesheet.reparse()
        stylesheet.update(self.app, animate=animate)
        self.screen._refresh_layout(self.size, full=True)

    def _display(self, screen: Screen, renderable: RenderableType | None) -> None:
        """Display a renderable within a sync.

        Args:
            screen (Screen): Screen instance
            renderable (RenderableType): A Rich renderable.
        """
        if screen is not self.screen or renderable is None:
            return
        if self._running and not self._closed and not self.is_headless:
            console = self.console
            self._begin_update()
            try:
                try:
                    console.print(renderable)
                except Exception as error:
                    self._handle_exception(error)
            finally:
                self._end_update()
            console.file.flush()

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
        if not self.is_headless:
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
        if isinstance(event, events.Compose):
            screen = Screen(id="_default")
            self._register(self, screen)
            self._screen_stack.append(screen)
            await super().on_event(event)

        elif isinstance(event, events.InputEvent) and not event.is_forwarded:
            if isinstance(event, events.MouseEvent):
                # Record current mouse position on App
                self.mouse_position = Offset(event.x, event.y)
            if isinstance(event, events.Key) and self.focused is not None:
                # Key events are sent direct to focused widget
                if self.bindings.allow_forward(event.key):
                    await self.focused._forward_event(event)
                else:
                    # Key has allow_forward=False which disallows forward to focused widget
                    await super().on_event(event)
            else:
                # Forward the event to the view
                await self.screen._forward_event(event)
        elif isinstance(event, events.Paste):
            if self.focused is not None:
                await self.focused._forward_event(event)
        else:
            await super().on_event(event)

    async def action(
        self,
        action: str | tuple[str, tuple[str, ...]],
        default_namespace: object | None = None,
    ) -> bool:
        """Perform an action.

        Args:
            action (str): Action encoded in a string.
            default_namespace (object | None): Namespace to use if not provided in the action,
                or None to use app. Defaults to None.

        Returns:
            bool: True if the event has handled.
        """
        if isinstance(action, str):
            target, params = actions.parse(action)
        else:
            target, params = action
        implicit_destination = True
        if "." in target:
            destination, action_name = target.split(".", 1)
            if destination not in self._action_targets:
                raise ActionError("Action namespace {destination} is not known")
            action_target = getattr(self, destination)
            implicit_destination = True
        else:
            action_target = default_namespace or self
            action_name = target

        handled = await self._dispatch_action(action_target, action_name, params)
        if not handled and implicit_destination and not isinstance(action_target, App):
            handled = await self.app._dispatch_action(self.app, action_name, params)
        return handled

    async def _dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> bool:
        log(
            "<action>",
            namespace=namespace,
            action_name=action_name,
            params=params,
        )
        _rich_traceback_guard = True
        method_name = f"action_{action_name}"
        method = getattr(namespace, method_name, None)
        if method is None:
            log(f"<action> {action_name!r} has no target")
        if callable(method):
            await invoke(method, *params)
            return True
        return False

    async def _broker_event(
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
        try:
            style = getattr(event, "style")
        except AttributeError:
            return False
        try:
            _modifiers, action = extract_handler_actions(event_name, style.meta)
        except NoHandler:
            return False
        else:
            event.stop()
        if isinstance(action, (str, tuple)):
            await self.action(action, default_namespace=default_namespace)
        elif callable(action):
            await action()
        else:
            return False
        return True

    async def _on_update(self, message: messages.Update) -> None:
        message.stop()

    async def _on_layout(self, message: messages.Layout) -> None:
        message.stop()

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            self.focus_next()
        elif event.key == "shift+tab":
            self.focus_previous()
        else:
            if not (await self.press(event.key)):
                await self.dispatch_key(event)

    async def _on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log("shutdown request")
        await self._close_messages()

    async def _on_resize(self, event: events.Resize) -> None:
        event.stop()
        self.screen._screen_resized(event.size)
        await self.screen.post_message(event)

    async def _on_remove(self, event: events.Remove) -> None:
        widget = event.widget
        parent = widget.parent
        if parent is not None:
            parent.refresh(layout=True)

        remove_widgets = list(widget.walk_children(Widget, with_self=True))
        for child in remove_widgets:
            self._unregister(child)
        for child in remove_widgets:
            await child._close_messages()

    async def action_press(self, key: str) -> None:
        await self.press(key)

    async def action_quit(self) -> None:
        """Quit the app as soon as possible."""
        await self.shutdown()

    async def action_bang(self) -> None:
        1 / 0

    async def action_bell(self) -> None:
        """Play the terminal 'bell'."""
        self.bell()

    async def action_focus(self, widget_id: str) -> None:
        """Focus the given widget.

        Args:
            widget_id (str): ID of widget to focus.
        """
        try:
            node = self.query(f"#{widget_id}").first()
        except NoMatchingNodesError:
            pass
        else:
            if isinstance(node, Widget):
                self.set_focus(node)

    async def action_switch_screen(self, screen: str) -> None:
        self.switch_screen(screen)

    async def action_push_screen(self, screen: str) -> None:
        self.push_screen(screen)

    async def action_pop_screen(self) -> None:
        self.pop_screen()

    async def action_back(self) -> None:
        try:
            self.pop_screen()
        except ScreenStackError:
            pass

    async def action_add_class_(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).add_class(class_name)

    async def action_remove_class_(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).remove_class(class_name)

    async def action_toggle_class(self, selector: str, class_name: str) -> None:
        self.screen.query(selector).toggle_class(class_name)

    def _on_terminal_supports_synchronized_output(
        self, message: messages.TerminalSupportsSynchronizedOutput
    ) -> None:
        log.system("[b green]SynchronizedOutput mode is supported")
        self._sync_available = True

    def _begin_update(self) -> None:
        if self._sync_available:
            self.console.file.write(SYNC_START)

    def _end_update(self) -> None:
        if self._sync_available:
            self.console.file.write(SYNC_END)


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
