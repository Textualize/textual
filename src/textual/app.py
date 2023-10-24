"""

Here you will find the [App][textual.app.App] class, which is the base class for Textual apps.

See [app basics](/guide/app) for how to build Textual apps.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import io
import os
import platform
import sys
import threading
import unicodedata
import warnings
from asyncio import Task
from concurrent.futures import Future
from contextlib import (
    asynccontextmanager,
    contextmanager,
    redirect_stderr,
    redirect_stdout,
)
from datetime import datetime
from functools import partial
from pathlib import PurePath
from time import perf_counter
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    ClassVar,
    Generator,
    Generic,
    Iterable,
    List,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from weakref import WeakKeyDictionary, WeakSet

import rich
import rich.repr
from rich import terminal_theme
from rich.console import Console, RenderableType
from rich.control import Control
from rich.protocol import is_renderable
from rich.segment import Segment, Segments
from rich.traceback import Traceback

from . import Logger, LogGroup, LogVerbosity, actions, constants, events, log, messages
from ._animator import DEFAULT_EASING, Animatable, Animator, EasingFunction
from ._ansi_sequences import SYNC_END, SYNC_START
from ._asyncio import create_task
from ._callback import invoke
from ._compose import compose
from ._compositor import CompositorUpdate
from ._context import active_app, active_message_pump
from ._context import message_hook as message_hook_context_var
from ._event_broker import NoHandler, extract_handler_actions
from ._path import CSSPathType, _css_path_type_as_list, _make_path_object_relative
from ._system_commands import SystemCommands
from ._wait import wait_for_idle
from ._worker_manager import WorkerManager
from .actions import ActionParseResult, SkipAction
from .await_remove import AwaitRemove
from .binding import Binding, BindingType, _Bindings
from .command import CommandPalette, Provider
from .css.query import NoMatches
from .css.stylesheet import Stylesheet
from .design import ColorSystem
from .dom import DOMNode
from .driver import Driver
from .drivers.headless_driver import HeadlessDriver
from .features import FeatureFlag, parse_features
from .file_monitor import FileMonitor
from .filter import ANSIToTruecolor, DimFilter, LineFilter, Monochrome
from .geometry import Offset, Region, Size
from .keys import (
    REPLACED_KEYS,
    _character_to_key,
    _get_key_display,
    _get_unicode_name_from_key,
)
from .messages import CallbackType
from .notifications import Notification, Notifications, Notify, SeverityLevel
from .reactive import Reactive
from .renderables.blank import Blank
from .screen import Screen, ScreenResultCallbackType, ScreenResultType
from .widget import AwaitMount, Widget
from .widgets._toast import ToastRack
from .worker import NoActiveWorker, get_current_worker

if TYPE_CHECKING:
    from textual_dev.client import DevtoolsClient
    from typing_extensions import Coroutine, Literal, TypeAlias

    from ._types import MessageTarget

    # Unused & ignored imports are needed for the docs to link to these objects:
    from .css.query import WrongType  # type: ignore  # noqa: F401
    from .message import Message
    from .pilot import Pilot
    from .widget import MountError  # type: ignore  # noqa: F401

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"

# asyncio will warn against resources not being cleared
if constants.DEBUG:
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

AutopilotCallbackType: TypeAlias = (
    "Callable[[Pilot[object]], Coroutine[Any, Any, None]]"
)
"""Signature for valid callbacks that can be used to control apps."""


class AppError(Exception):
    """Base class for general App related exceptions."""


class ActionError(Exception):
    """Base class for exceptions relating to actions."""


class ScreenError(Exception):
    """Base class for exceptions that relate to screens."""


class ScreenStackError(ScreenError):
    """Raised when trying to manipulate the screen stack incorrectly."""


class ModeError(Exception):
    """Base class for exceptions related to modes."""


class InvalidModeError(ModeError):
    """Raised if there is an issue with a mode name."""


class UnknownModeError(ModeError):
    """Raised when attempting to use a mode that is not known."""


class ActiveModeError(ModeError):
    """Raised when attempting to remove the currently active mode."""


ReturnType = TypeVar("ReturnType")

CSSPathType = Union[
    str,
    PurePath,
    List[Union[str, PurePath]],
]
"""Valid ways of specifying paths to CSS files."""

CallThreadReturnType = TypeVar("CallThreadReturnType")


class _NullFile:
    """A file-like where writes go nowhere."""

    def write(self, text: str) -> None:
        pass

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return True


class _PrintCapture:
    """A file-like which captures output."""

    def __init__(self, app: App, stderr: bool = False) -> None:
        """

        Args:
            app: App instance.
            stderr: Write from stderr.
        """
        self.app = app
        self.stderr = stderr

    def write(self, text: str) -> None:
        """Called when writing to stdout or stderr.

        Args:
            text: Text that was "printed".
        """
        self.app._print(text, stderr=self.stderr)

    def flush(self) -> None:
        """Called when stdout or stderr was flushed."""
        self.app._flush(stderr=self.stderr)

    def isatty(self) -> bool:
        """Pretend we're a terminal."""
        # TODO: should this be configurable?
        return True

    def fileno(self) -> int:
        """Return invalid fileno."""
        return -1


@rich.repr.auto
class App(Generic[ReturnType], DOMNode):
    """The base class for Textual Applications."""

    CSS: ClassVar[str] = ""
    """Inline CSS, useful for quick scripts. This is loaded after CSS_PATH,
    and therefore takes priority in the event of a specificity clash."""

    # Default (the lowest priority) CSS
    DEFAULT_CSS: ClassVar[str]
    DEFAULT_CSS = """
    App {
        background: $background;
        color: $text;
    }
    *:disabled:can-focus {
        opacity: 0.7;
    }
    """

    MODES: ClassVar[dict[str, str | Screen | Callable[[], Screen]]] = {}
    """Modes associated with the app and their base screens.

    The base screen is the screen at the bottom of the mode stack. You can think of
    it as the default screen for that stack.
    The base screens can be names of screens listed in [SCREENS][textual.app.App.SCREENS],
    [`Screen`][textual.screen.Screen] instances, or callables that return screens.

    Example:
        ```py
        class HelpScreen(Screen[None]):
            ...

        class MainAppScreen(Screen[None]):
            ...

        class MyApp(App[None]):
            MODES = {
                "default": "main",
                "help": HelpScreen,
            }

            SCREENS = {
                "main": MainAppScreen,
            }

            ...
        ```
    """
    SCREENS: ClassVar[dict[str, Screen | Callable[[], Screen]]] = {}
    """Screens associated with the app for the lifetime of the app."""

    AUTO_FOCUS: ClassVar[str | None] = "*"
    """A selector to determine what to focus automatically when a screen is activated.

    The widget focused is the first that matches the given [CSS selector](/guide/queries/#query-selectors).
    Setting to `None` or `""` disables auto focus.
    """

    _BASE_PATH: str | None = None
    CSS_PATH: ClassVar[CSSPathType | None] = None
    """File paths to load CSS from."""

    TITLE: str | None = None
    """A class variable to set the *default* title for the application.

    To update the title while the app is running, you can set the [title][textual.app.App.title] attribute.
    See also [the `Screen.TITLE` attribute][textual.screen.Screen.TITLE].
    """

    SUB_TITLE: str | None = None
    """A class variable to set the default sub-title for the application.

    To update the sub-title while the app is running, you can set the [sub_title][textual.app.App.sub_title] attribute.
    See also [the `Screen.SUB_TITLE` attribute][textual.screen.Screen.SUB_TITLE].
    """

    ENABLE_COMMAND_PALETTE: ClassVar[bool] = True
    """Should the [command palette][textual.command.CommandPalette] be enabled for the application?"""

    COMMANDS: ClassVar[set[type[Provider]]] = {SystemCommands}
    """Command providers used by the [command palette](/guide/command_palette).

    Should be a set of [command.Provider][textual.command.Provider] classes.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+backslash", "command_palette", show=False, priority=True),
    ]

    title: Reactive[str] = Reactive("", compute=False)
    sub_title: Reactive[str] = Reactive("", compute=False)

    dark: Reactive[bool] = Reactive(True, compute=False)
    """Use a dark theme if `True`, otherwise use a light theme.

    Modify this attribute to switch between light and dark themes.

    Example:
        ```python
        self.app.dark = not self.app.dark  # Toggle dark mode
        ```
    """

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ):
        """Create an instance of an app.

        Args:
            driver_class: Driver class or `None` to auto-detect.
                This will be used by some Textual tools.
            css_path: Path to CSS or `None` to use the `CSS_PATH` class variable.
                To load multiple CSS files, pass a list of strings or paths which
                will be loaded in order.
            watch_css: Reload CSS if the files changed. This is set automatically if
                you are using `textual run` with the `dev` switch.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        self._start_time = perf_counter()
        super().__init__()
        self.features: frozenset[FeatureFlag] = parse_features(os.getenv("TEXTUAL", ""))

        self._filters: list[LineFilter] = []
        environ = dict(os.environ)
        no_color = environ.pop("NO_COLOR", None)
        if no_color is not None:
            self._filters.append(Monochrome())

        for filter_name in constants.FILTERS.split(","):
            filter = filter_name.lower().strip()
            if filter == "dim":
                self._filters.append(ANSIToTruecolor(terminal_theme.DIMMED_MONOKAI))
                self._filters.append(DimFilter())

        self.console = Console(
            color_system=constants.COLOR_SYSTEM,
            file=_NullFile(),
            markup=True,
            highlight=False,
            emoji=False,
            legacy_windows=False,
            _environ=environ,
            force_terminal=True,
            safe_box=False,
        )
        self._workers = WorkerManager(self)
        self.error_console = Console(markup=False, stderr=True)
        self.driver_class = driver_class or self.get_driver_class()
        self._screen_stacks: dict[str, list[Screen]] = {"_default": []}
        """A stack of screens per mode."""
        self._current_mode: str = "_default"
        """The current mode the app is in."""
        self._sync_available = False

        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._action_targets = {"app", "screen"}
        self._animator = Animator(self)
        self._animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)

        self.cursor_position = Offset(0, 0)
        """The position of the terminal cursor in screen-space.

        This can be set by widgets and is useful for controlling the
        positioning of OS IME and emoji popup menus."""

        self._exception: Exception | None = None
        """The unhandled exception which is leading to the app shutting down,
        or None if the app is still running with no unhandled exceptions."""

        self._exception_event: asyncio.Event = asyncio.Event()
        """An event that will be set when the first exception is encountered."""

        self.title = (
            self.TITLE if self.TITLE is not None else f"{self.__class__.__name__}"
        )
        """The title for the application.

        The initial value for `title` will be set to the `TITLE` class variable if it exists, or
        the name of the app if it doesn't.

        Assign a new value to this attribute to change the title.
        The new value is always converted to string.
        """

        self.sub_title = self.SUB_TITLE if self.SUB_TITLE is not None else ""
        """The sub-title for the application.

        The initial value for `sub_title` will be set to the `SUB_TITLE` class variable if it exists, or
        an empty string if it doesn't.

        Sub-titles are typically used to show the high-level state of the app, such as the current mode, or path to
        the file being worked on.

        Assign a new value to this attribute to change the sub-title.
        The new value is always converted to string.
        """

        self.use_command_palette: bool = self.ENABLE_COMMAND_PALETTE
        """A flag to say if the application should use the command palette.

        If set to `False` any call to
        [`action_command_palette`][textual.app.App.action_command_palette]
        will be ignored.
        """

        self._logger = Logger(self._log)

        self._refresh_required = False

        self.design = DEFAULT_COLORS

        self._css_has_errors = False
        self.stylesheet = Stylesheet(variables=self.get_css_variables())

        css_path = css_path or self.CSS_PATH
        css_paths = [
            _make_path_object_relative(css_path, self)
            for css_path in (
                _css_path_type_as_list(css_path) if css_path is not None else []
            )
        ]
        self.css_path = css_paths

        self._registry: WeakSet[DOMNode] = WeakSet()

        # Sensitivity on X is double the sensitivity on Y to account for
        # cells being twice as tall as wide
        self.scroll_sensitivity_x: float = 4.0
        """Number of columns to scroll in the X direction with wheel or trackpad."""
        self.scroll_sensitivity_y: float = 2.0
        """Number of lines to scroll in the Y direction with wheel or trackpad."""

        self._installed_screens: dict[str, Screen | Callable[[], Screen]] = {}
        self._installed_screens.update(**self.SCREENS)

        self._compose_stacks: list[list[Widget]] = []
        self._composed: list[list[Widget]] = []

        self.devtools: DevtoolsClient | None = None
        self._devtools_redirector: StdoutRedirector | None = None
        if "devtools" in self.features:
            try:
                from textual_dev.client import DevtoolsClient
                from textual_dev.redirect_output import StdoutRedirector
            except ImportError:
                # Dev dependencies not installed
                pass
            else:
                self.devtools = DevtoolsClient(constants.DEVTOOLS_HOST)
                self._devtools_redirector = StdoutRedirector(self.devtools)

        self._loop: asyncio.AbstractEventLoop | None = None
        self._return_value: ReturnType | None = None
        """Internal attribute used to set the return value for the app."""
        self._return_code: int | None = None
        """Internal attribute used to set the return code for the app."""
        self._exit = False
        self._disable_tooltips = False
        self._disable_notifications = False

        self.css_monitor = (
            FileMonitor(self.css_path, self._on_css_change)
            if ((watch_css or self.debug) and self.css_path)
            else None
        )
        self._screenshot: str | None = None
        self._dom_lock = asyncio.Lock()
        self._dom_ready = False
        self._batch_count = 0
        self._notifications = Notifications()

        self._capture_print: WeakKeyDictionary[
            MessageTarget, tuple[bool, bool]
        ] = WeakKeyDictionary()
        """Registry of the MessageTargets which are capturing output at any given time."""
        self._capture_stdout = _PrintCapture(self, stderr=False)
        """File-like object capturing data written to stdout."""
        self._capture_stderr = _PrintCapture(self, stderr=True)
        """File-like object capturing data written to stderr."""
        self._original_stdout = sys.__stdout__
        """The original stdout stream (before redirection etc)."""
        self._original_stderr = sys.__stderr__
        """The original stderr stream (before redirection etc)."""

        self.set_class(self.dark, "-dark-mode")
        self.set_class(not self.dark, "-light-mode")

    def validate_title(self, title: Any) -> str:
        """Make sure the title is set to a string."""
        return str(title)

    def validate_sub_title(self, sub_title: Any) -> str:
        """Make sure the sub-title is set to a string."""
        return str(sub_title)

    @property
    def workers(self) -> WorkerManager:
        """The [worker](guide/workers/) manager.

        Returns:
            An object to manage workers.
        """
        return self._workers

    @property
    def return_value(self) -> ReturnType | None:
        """The return value of the app, or `None` if it has not yet been set.

        The return value is set when calling [exit][textual.app.App.exit].
        """
        return self._return_value

    @property
    def return_code(self) -> int | None:
        """The return code with which the app exited.

        Non-zero codes indicate errors.
        A value of 1 means the app exited with a fatal error.
        If the app wasn't exited yet, this will be `None`.

        Example:
            The return code can be used to exit the process via `sys.exit`.
            ```py
            my_app.run()
            sys.exit(my_app.return_code)
            ```
        """
        return self._return_code

    @property
    def children(self) -> Sequence["Widget"]:
        """A view onto the app's immediate children.

        This attribute exists on all widgets.
        In the case of the App, it will only ever contain a single child, which will
        be the currently active screen.

        Returns:
            A sequence of widgets.
        """
        try:
            return (self.screen,)
        except ScreenError:
            return ()

    @contextmanager
    def batch_update(self) -> Generator[None, None, None]:
        """A context manager to suspend all repaints until the end of the batch."""
        self._begin_batch()
        try:
            yield
        finally:
            self._end_batch()

    def _begin_batch(self) -> None:
        """Begin a batch update."""
        self._batch_count += 1

    def _end_batch(self) -> None:
        """End a batch update."""
        self._batch_count -= 1
        assert self._batch_count >= 0, "This won't happen if you use `batch_update`"
        if not self._batch_count:
            self.check_idle()

    def animate(
        self,
        attribute: str,
        value: float | Animatable,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        delay: float = 0.0,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Animate an attribute.

        See the guide for how to use the [animation](/guide/animation) system.

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation.
            duration: The duration of the animate.
            speed: The speed of the animation.
            delay: A delay (in seconds) before the animation starts.
            easing: An easing method.
            on_complete: A callable to invoke when the animation is finished.
        """
        self._animate(
            attribute,
            value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            delay=delay,
            easing=easing,
            on_complete=on_complete,
        )

    async def stop_animation(self, attribute: str, complete: bool = True) -> None:
        """Stop an animation on an attribute.

        Args:
            attribute: Name of the attribute whose animation should be stopped.
            complete: Should the animation be set to its final value?

        Note:
            If there is no animation scheduled or running, this is a no-op.
        """
        await self._animator.stop_animation(self, attribute, complete)

    @property
    def debug(self) -> bool:
        """Is debug mode enabled?"""
        return "debug" in self.features

    @property
    def is_headless(self) -> bool:
        """Is the driver running in 'headless' mode?

        Headless mode is used when running tests with [run_test][textual.app.App.run_test].
        """
        return False if self._driver is None else self._driver.is_headless

    @property
    def screen_stack(self) -> Sequence[Screen]:
        """A snapshot of the current screen stack.

        Returns:
            A snapshot of the current state of the screen stack.
        """
        return self._screen_stacks[self._current_mode].copy()

    @property
    def _screen_stack(self) -> list[Screen]:
        """A reference to the current screen stack.

        Note:
            Consider using [`screen_stack`][textual.app.App.screen_stack] instead.

        Returns:
            A reference to the current screen stack.
        """
        return self._screen_stacks[self._current_mode]

    @property
    def current_mode(self) -> str:
        """The name of the currently active mode."""
        return self._current_mode

    def exit(
        self,
        result: ReturnType | None = None,
        return_code: int = 0,
        message: RenderableType | None = None,
    ) -> None:
        """Exit the app, and return the supplied result.

        Args:
            result: Return value.
            return_code: The return code. Use non-zero values for error codes.
            message: Optional message to display on exit.
        """
        self._exit = True
        self._return_value = result
        self._return_code = return_code
        self.post_message(messages.ExitApp())
        if message:
            self._exit_renderables.append(message)

    @property
    def focused(self) -> Widget | None:
        """The widget that is focused on the currently active screen, or `None`.

        Focused widgets receive keyboard input.

        Returns:
            The currently focused widget, or `None` if nothing is focused.
        """
        return self.screen.focused

    @property
    def namespace_bindings(self) -> dict[str, tuple[DOMNode, Binding]]:
        """Get currently active bindings.

        If no widget is focused, then app-level bindings are returned.
        If a widget is focused, then any bindings present in the active screen and app are merged and returned.

        This property may be used to inspect current bindings.

        Returns:
            A mapping of keys onto pairs of nodes and bindings.
        """

        namespace_binding_map: dict[str, tuple[DOMNode, Binding]] = {}
        for namespace, bindings in reversed(self._binding_chain):
            for key, binding in bindings.keys.items():
                namespace_binding_map[key] = (namespace, binding)

        return namespace_binding_map

    def _set_active(self) -> None:
        """Set this app to be the currently active app."""
        active_app.set(self)

    def compose(self) -> ComposeResult:
        """Yield child widgets for a container.

        This method should be implemented in a subclass.
        """
        yield from ()

    def get_css_variables(self) -> dict[str, str]:
        """Get a mapping of variables used to pre-populate CSS.

        May be implemented in a subclass to add new CSS variables.

        Returns:
            A mapping of variable name to value.
        """
        variables = self.design["dark" if self.dark else "light"].generate()
        return variables

    def watch_dark(self, dark: bool) -> None:
        """Watches the dark bool.

        This method handles the transition between light and dark mode when you
        change the [dark][textual.app.App.dark] attribute.
        """
        self.set_class(dark, "-dark-mode")
        self.set_class(not dark, "-light-mode")
        self.call_later(self.refresh_css)

    def get_driver_class(self) -> Type[Driver]:
        """Get a driver class for this platform.

        This method is called by the constructor, and unlikely to be required when
        building a Textual app.

        Returns:
            A Driver class which manages input and display.
        """

        driver_class: Type[Driver]

        driver_import = constants.DRIVER
        if driver_import is not None:
            # The driver class is set from the environment
            # Syntax should be foo.bar.baz:MyDriver
            module_import, _, driver_symbol = driver_import.partition(":")
            driver_module = importlib.import_module(module_import)
            driver_class = getattr(driver_module, driver_symbol)
            if not inspect.isclass(driver_class) or not issubclass(
                driver_class, Driver
            ):
                raise RuntimeError(
                    f"Unable to import {driver_import!r}; {driver_class!r} is not a Driver class "
                )
            return driver_class

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
    def animator(self) -> Animator:
        return self._animator

    @property
    def screen(self) -> Screen[object]:
        """The current active screen.

        Returns:
            The currently active (visible) screen.

        Raises:
            ScreenStackError: If there are no screens on the stack.
        """
        try:
            return self._screen_stack[-1]
        except KeyError:
            raise UnknownModeError(f"No known mode {self._current_mode!r}") from None
        except IndexError:
            raise ScreenStackError("No screens on stack") from None

    @property
    def _background_screens(self) -> list[Screen]:
        """A list of screens that may be visible due to background opacity (top-most first, not including current screen)."""
        screens: list[Screen] = []
        for screen in reversed(self._screen_stack[:-1]):
            screens.append(screen)
            if screen.styles.background.a == 1:
                break
        background_screens = screens[::-1]
        return background_screens

    @property
    def size(self) -> Size:
        """The size of the terminal.

        Returns:
            Size of the terminal.
        """
        if self._driver is not None and self._driver._size is not None:
            width, height = self._driver._size
        else:
            width, height = self.console.size
        return Size(width, height)

    @property
    def log(self) -> Logger:
        """The textual logger.

        Example:
            ```python
            self.log("Hello, World!")
            self.log(self.tree)
            ```

        Returns:
            A Textual logger.
        """
        return self._logger

    def _log(
        self,
        group: LogGroup,
        verbosity: LogVerbosity,
        _textual_calling_frame: inspect.Traceback,
        *objects: Any,
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
            verbosity: Verbosity level 0-3.
        """

        devtools = self.devtools
        if devtools is None or not devtools.is_connected:
            return

        if verbosity.value > LogVerbosity.NORMAL.value and not devtools.verbose:
            return

        try:
            from textual_dev.client import DevtoolsLog

            if len(objects) == 1 and not kwargs:
                devtools.log(
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
                devtools.log(
                    DevtoolsLog(output, caller=_textual_calling_frame),
                    group,
                    verbosity,
                )
        except Exception as error:
            self._handle_exception(error)

    def call_from_thread(
        self,
        callback: Callable[..., CallThreadReturnType | Awaitable[CallThreadReturnType]],
        *args: object,
        **kwargs: object,
    ) -> CallThreadReturnType:
        """Run a callable from another thread, and return the result.

        Like asyncio apps in general, Textual apps are not thread-safe. If you call methods
        or set attributes on Textual objects from a thread, you may get unpredictable results.

        This method will ensure that your code runs within the correct context.

        !!! tip

            Consider using [post_message][textual.message_pump.MessagePump.post_message] which is also thread-safe.

        Args:
            callback: A callable to run.
            *args: Arguments to the callback.
            **kwargs: Keyword arguments for the callback.

        Raises:
            RuntimeError: If the app isn't running or if this method is called from the same
                thread where the app is running.

        Returns:
            The result of the callback.
        """

        if self._loop is None:
            raise RuntimeError("App is not running")

        if self._thread_id == threading.get_ident():
            raise RuntimeError(
                "The `call_from_thread` method must run in a different thread from the app"
            )

        callback_with_args = partial(callback, *args, **kwargs)

        async def run_callback() -> CallThreadReturnType:
            """Run the callback, set the result or error on the future."""
            self._set_active()
            return await invoke(callback_with_args)

        # Post the message to the main loop
        future: Future[CallThreadReturnType] = asyncio.run_coroutine_threadsafe(
            run_callback(), loop=self._loop
        )
        result = future.result()
        return result

    def action_toggle_dark(self) -> None:
        """An [action](/guide/actions) to toggle dark mode."""
        self.dark = not self.dark

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        """This [action](/guide/actions) will save an SVG file containing the current contents of the screen.

        Args:
            filename: Filename of screenshot, or None to auto-generate.
            path: Path to directory. Defaults to current working directory.
        """
        self.save_screenshot(filename, path)

    def export_screenshot(self, *, title: str | None = None) -> str:
        """Export an SVG screenshot of the current screen.

        See also [save_screenshot][textual.app.App.save_screenshot] which writes the screenshot to a file.

        Args:
            title: The title of the exported screenshot or None
                to use app title.
        """
        assert self._driver is not None, "App must be running"
        width, height = self.size

        console = Console(
            width=width,
            height=height,
            file=io.StringIO(),
            force_terminal=True,
            color_system="truecolor",
            record=True,
            legacy_windows=False,
            safe_box=False,
        )
        screen_render = self.screen._compositor.render_update(
            full=True, screen_stack=self.app._background_screens
        )
        console.print(screen_render)
        return console.export_svg(title=title or self.title)

    def save_screenshot(
        self,
        filename: str | None = None,
        path: str = "./",
        time_format: str | None = None,
    ) -> str:
        """Save an SVG screenshot of the current screen.

        Args:
            filename: Filename of SVG screenshot, or None to auto-generate
                a filename with the date and time.
            path: Path to directory for output. Defaults to current working directory.
            time_format: Date and time format to use if filename is None.
                Defaults to a format like ISO 8601 with some reserved characters replaced with underscores.

        Returns:
            Filename of screenshot.
        """
        if filename is None:
            if time_format is None:
                dt = datetime.now().isoformat()
            else:
                dt = datetime.now().strftime(time_format)
            svg_filename_stem = f"{self.title.lower()} {dt}"
            for reserved in ' <>:"/\\|?*.':
                svg_filename_stem = svg_filename_stem.replace(reserved, "_")
            svg_filename = svg_filename_stem + ".svg"
        else:
            svg_filename = filename
        svg_path = os.path.expanduser(os.path.join(path, svg_filename))
        screenshot_svg = self.export_screenshot()
        with open(svg_path, "w", encoding="utf-8") as svg_file:
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
            keys: A comma separated list of keys, i.e.
            action: Action to bind to.
            description: Short description of action.
            show: Show key in UI.
            key_display: Replacement text for key, or None to use default.
        """
        self._bindings.bind(
            keys, action, description, show=show, key_display=key_display
        )

    def get_key_display(self, key: str) -> str:
        """For a given key, return how it should be displayed in an app
        (e.g. in the Footer widget).
        By key, we refer to the string used in the "key" argument for
        a Binding instance. By overriding this method, you can ensure that
        keys are displayed consistently throughout your app, without
        needing to add a key_display to every binding.

        Args:
            key: The binding key string.

        Returns:
            The display string for the input key.
        """
        return _get_key_display(key)

    async def _press_keys(self, keys: Iterable[str]) -> None:
        """A task to send key events."""
        app = self
        driver = app._driver
        assert driver is not None
        for key in keys:
            if key.startswith("wait:"):
                _, wait_ms = key.split(":")
                print(f"(pause {wait_ms}ms)")
                await asyncio.sleep(float(wait_ms) / 1000)
            else:
                if len(key) == 1 and not key.isalnum():
                    key = _character_to_key(key)
                original_key = REPLACED_KEYS.get(key, key)
                char: str | None
                try:
                    char = unicodedata.lookup(_get_unicode_name_from_key(original_key))
                except KeyError:
                    char = key if len(key) == 1 else None
                print(f"press {key!r} (char={char!r})")
                key_event = events.Key(key, char)
                key_event._set_sender(app)
                driver.send_event(key_event)
                await wait_for_idle(0)
                await app._animator.wait_until_complete()
                await wait_for_idle(0)

    def _flush(self, stderr: bool = False) -> None:
        """Called when stdout or stderr is flushed.

        Args:
            stderr: True if the print was to stderr, or False for stdout.

        """
        if self._devtools_redirector is not None:
            self._devtools_redirector.flush()

    def _print(self, text: str, stderr: bool = False) -> None:
        """Called with captured print.

        Dispatches printed content to appropriate destinations: devtools,
        widgets currently capturing output, stdout/stderr.

        Args:
            text: Text that has been printed.
            stderr: True if the print was to stderr, or False for stdout.
        """
        if self._devtools_redirector is not None:
            current_frame = inspect.currentframe()
            self._devtools_redirector.write(
                text, current_frame.f_back if current_frame is not None else None
            )

        # If we're in headless mode, we want printed text to still reach stdout/stderr.
        if self.is_headless:
            target_stream = self._original_stderr if stderr else self._original_stdout
            target_stream.write(text)

        # Send Print events to all widgets that are currently capturing output.
        for target, (_stdout, _stderr) in self._capture_print.items():
            if (_stderr and stderr) or (_stdout and not stderr):
                target.post_message(events.Print(text, stderr=stderr))

    def begin_capture_print(
        self, target: MessageTarget, stdout: bool = True, stderr: bool = True
    ) -> None:
        """Capture content that is printed (or written to stdout / stderr).

        If printing is captured, the `target` will be sent an [events.Print][textual.events.Print] message.

        Args:
            target: The widget where print content will be sent.
            stdout: Capture stdout.
            stderr: Capture stderr.
        """
        if not stdout and not stderr:
            self.end_capture_print(target)
        else:
            self._capture_print[target] = (stdout, stderr)

    def end_capture_print(self, target: MessageTarget) -> None:
        """End capturing of prints.

        Args:
            target: The widget that was capturing prints.
        """
        self._capture_print.pop(target)

    @asynccontextmanager
    async def run_test(
        self,
        *,
        headless: bool = True,
        size: tuple[int, int] | None = (80, 24),
        tooltips: bool = False,
        notifications: bool = False,
        message_hook: Callable[[Message], None] | None = None,
    ) -> AsyncGenerator[Pilot[ReturnType], None]:
        """An asynchronous context manager for testing apps.

        !!! tip

            See the guide for [testing](/guide/testing) Textual apps.

        Use this to run your app in "headless" mode (no output) and drive the app via a [Pilot][textual.pilot.Pilot] object.

        Example:

            ```python
            async with app.run_test() as pilot:
                await pilot.click("#Button.ok")
                assert ...
            ```

        Args:
            headless: Run in headless mode (no output or input).
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect.
            tooltips: Enable tooltips when testing.
            notifications: Enable notifications when testing.
            message_hook: An optional callback that will be called each time any message arrives at any
                message pump in the app.
        """
        from .pilot import Pilot

        app = self
        app._disable_tooltips = not tooltips
        app._disable_notifications = not notifications
        app_ready_event = asyncio.Event()

        def on_app_ready() -> None:
            """Called when app is ready to process events."""
            app_ready_event.set()

        async def run_app(app: App) -> None:
            if message_hook is not None:
                message_hook_context_var.set(message_hook)
            app._loop = asyncio.get_running_loop()
            app._thread_id = threading.get_ident()
            await app._process_messages(
                ready_callback=on_app_ready,
                headless=headless,
                terminal_size=size,
            )

        # Launch the app in the "background"
        active_message_pump.set(app)
        app_task = create_task(run_app(app), name=f"run_test {app}")

        # Wait until the app has performed all startup routines.
        await app_ready_event.wait()

        # Get the app in an active state.
        app._set_active()

        # Context manager returns pilot object to manipulate the app
        try:
            pilot = Pilot(app)
            await pilot._wait_for_screen()
            yield pilot
        finally:
            # Shutdown the app cleanly
            await app._shutdown()
            await app_task
            # Re-raise the exception which caused panic so test frameworks are aware
            if self._exception:
                raise self._exception

    async def run_async(
        self,
        *,
        headless: bool = False,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> ReturnType | None:
        """Run the app asynchronously.

        Args:
            headless: Run in headless mode (no output).
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect.
            auto_pilot: An auto pilot coroutine.

        Returns:
            App return value.
        """
        from .pilot import Pilot

        app = self

        auto_pilot_task: Task | None = None

        if auto_pilot is None and constants.PRESS:
            keys = constants.PRESS.split(",")

            async def press_keys(pilot: Pilot) -> None:
                """Auto press keys."""
                await pilot.press(*keys)

            auto_pilot = press_keys

        async def app_ready() -> None:
            """Called by the message loop when the app is ready."""
            nonlocal auto_pilot_task

            if auto_pilot is not None:

                async def run_auto_pilot(
                    auto_pilot: AutopilotCallbackType, pilot: Pilot
                ) -> None:
                    try:
                        await auto_pilot(pilot)
                    except Exception:
                        app.exit()
                        raise

                pilot = Pilot(app)
                active_message_pump.set(self)
                auto_pilot_task = create_task(
                    run_auto_pilot(auto_pilot, pilot), name=repr(pilot)
                )

        try:
            app._loop = asyncio.get_running_loop()
            app._thread_id = threading.get_ident()

            await app._process_messages(
                ready_callback=None if auto_pilot is None else app_ready,
                headless=headless,
                terminal_size=size,
            )
        finally:
            try:
                if auto_pilot_task is not None:
                    await auto_pilot_task
            finally:
                await app._shutdown()

        return app.return_value

    def run(
        self,
        *,
        headless: bool = False,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> ReturnType | None:
        """Run the app.

        Args:
            headless: Run in headless mode (no output).
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect.
            auto_pilot: An auto pilot coroutine.

        Returns:
            App return value.
        """

        async def run_app() -> None:
            """Run the app."""
            self._loop = asyncio.get_running_loop()
            self._thread_id = threading.get_ident()
            try:
                await self.run_async(
                    headless=headless,
                    size=size,
                    auto_pilot=auto_pilot,
                )
            finally:
                self._loop = None
                self._thread_id = 0

        if _ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED:
            # N.B. This doesn't work with Python<3.10, as we end up with 2 event loops:
            asyncio.run(run_app())
        else:
            # However, this works with Python<3.10:
            event_loop = asyncio.get_event_loop()
            event_loop.run_until_complete(run_app())
        return self.return_value

    async def _on_css_change(self) -> None:
        """Called when the CSS changes (if watch_css is True)."""
        css_paths = self.css_path
        if css_paths:
            try:
                time = perf_counter()
                stylesheet = self.stylesheet.copy()
                stylesheet.read_all(css_paths)
                stylesheet.parse()
                elapsed = (perf_counter() - time) * 1000
                if self._css_has_errors:
                    from rich.panel import Panel

                    self.log.system(
                        Panel(
                            "CSS files successfully loaded after previous error:\n\n- "
                            + "\n- ".join(str(path) for path in css_paths),
                            style="green",
                            border_style="green",
                        )
                    )
                self.log.system(
                    f"<stylesheet> loaded {len(css_paths)} CSS files in {elapsed:.0f} ms"
                )
            except Exception as error:
                # TODO: Catch specific exceptions
                self._css_has_errors = True
                self.log.error(error)
                self.bell()
            else:
                self._css_has_errors = False
                self.stylesheet = stylesheet
                self.stylesheet.update(self)
                self.screen.refresh(layout=True)

    def render(self) -> RenderableType:
        return Blank(self.styles.background)

    ExpectType = TypeVar("ExpectType", bound=Widget)

    @overload
    def get_child_by_id(self, id: str) -> Widget:
        ...

    @overload
    def get_child_by_id(self, id: str, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def get_child_by_id(
        self, id: str, expect_type: type[ExpectType] | None = None
    ) -> ExpectType | Widget:
        """Get the first child (immediate descendent) of this DOMNode with the given ID.

        Args:
            id: The ID of the node to search for.
            expect_type: Require the object be of the supplied type,
                or use `None` to apply no type restriction.

        Returns:
            The first child of this node with the specified ID.

        Raises:
            NoMatches: If no children could be found for this ID.
            WrongType: If the wrong type was found.
        """
        return (
            self.screen.get_child_by_id(id)
            if expect_type is None
            else self.screen.get_child_by_id(id, expect_type)
        )

    @overload
    def get_widget_by_id(self, id: str) -> Widget:
        ...

    @overload
    def get_widget_by_id(self, id: str, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def get_widget_by_id(
        self, id: str, expect_type: type[ExpectType] | None = None
    ) -> ExpectType | Widget:
        """Get the first descendant widget with the given ID.

        Performs a breadth-first search rooted at the current screen.
        It will not return the Screen if that matches the ID.
        To get the screen, use `self.screen`.

        Args:
            id: The ID to search for in the subtree
            expect_type: Require the object be of the supplied type, or None for any type.
                Defaults to None.

        Returns:
            The first descendant encountered with this ID.

        Raises:
            NoMatches: if no children could be found for this ID
            WrongType: if the wrong type was found.
        """
        return (
            self.screen.get_widget_by_id(id)
            if expect_type is None
            else self.screen.get_widget_by_id(id, expect_type)
        )

    def get_child_by_type(self, expect_type: type[ExpectType]) -> ExpectType:
        """Get a child of a give type.

        Args:
            expect_type: The type of the expected child.

        Raises:
            NoMatches: If no valid child is found.

        Returns:
            A widget.
        """
        return self.screen.get_child_by_type(expect_type)

    def update_styles(self, node: DOMNode) -> None:
        """Immediately update the styles of this node and all descendant nodes.

        Should be called whenever CSS classes / pseudo classes change.
        For example, when you hover over a button, the :hover pseudo class
        will be added, and this method is called to apply the corresponding
        :hover styles.
        """

        descendants = node.walk_children(with_self=True)
        self.stylesheet.update_nodes(descendants, animate=True)

    def mount(
        self,
        *widgets: Widget,
        before: int | str | Widget | None = None,
        after: int | str | Widget | None = None,
    ) -> AwaitMount:
        """Mount the given widgets relative to the app's screen.

        Args:
            *widgets: The widget(s) to mount.
            before: Optional location to mount before. An `int` is the index
                of the child to mount before, a `str` is a `query_one` query to
                find the widget to mount before.
            after: Optional location to mount after. An `int` is the index
                of the child to mount after, a `str` is a `query_one` query to
                find the widget to mount after.

        Returns:
            An awaitable object that waits for widgets to be mounted.

        Raises:
            MountError: If there is a problem with the mount request.

        Note:
            Only one of ``before`` or ``after`` can be provided. If both are
            provided a ``MountError`` will be raised.
        """
        return self.screen.mount(*widgets, before=before, after=after)

    def mount_all(
        self,
        widgets: Iterable[Widget],
        *,
        before: int | str | Widget | None = None,
        after: int | str | Widget | None = None,
    ) -> AwaitMount:
        """Mount widgets from an iterable.

        Args:
            widgets: An iterable of widgets.
            before: Optional location to mount before. An `int` is the index
                of the child to mount before, a `str` is a `query_one` query to
                find the widget to mount before.
            after: Optional location to mount after. An `int` is the index
                of the child to mount after, a `str` is a `query_one` query to
                find the widget to mount after.

        Returns:
            An awaitable object that waits for widgets to be mounted.

        Raises:
            MountError: If there is a problem with the mount request.

        Note:
            Only one of ``before`` or ``after`` can be provided. If both are
            provided a ``MountError`` will be raised.
        """
        return self.mount(*widgets, before=before, after=after)

    def _init_mode(self, mode: str) -> AwaitMount:
        """Do internal initialisation of a new screen stack mode.

        Args:
            mode: Name of the mode.

        Returns:
            An optionally awaitable object which can be awaited until the screen
            associated with the mode has been mounted.
        """

        stack = self._screen_stacks.get(mode, [])
        if stack:
            await_mount = AwaitMount(stack[0], [])
        else:
            _screen = self.MODES[mode]
            new_screen: Screen | str = _screen() if callable(_screen) else _screen
            screen, await_mount = self._get_screen(new_screen)
            stack.append(screen)
            self._load_screen_css(screen)

        self._screen_stacks[mode] = stack
        return await_mount

    def switch_mode(self, mode: str) -> AwaitMount:
        """Switch to a given mode.

        Args:
            mode: The mode to switch to.

        Returns:
            An optionally awaitable object which waits for the screen associated
                with the mode to be mounted.

        Raises:
            UnknownModeError: If trying to switch to an unknown mode.
        """
        if mode not in self.MODES:
            raise UnknownModeError(f"No known mode {mode!r}")

        self.screen.post_message(events.ScreenSuspend())
        self.screen.refresh()

        if mode not in self._screen_stacks:
            await_mount = self._init_mode(mode)
        else:
            await_mount = AwaitMount(self.screen, [])

        self._current_mode = mode
        self.screen._screen_resized(self.size)
        self.screen.post_message(events.ScreenResume())

        self.log.system(f"{self._current_mode!r} is the current mode")
        self.log.system(f"{self.screen} is active")

        return await_mount

    def add_mode(
        self, mode: str, base_screen: str | Screen | Callable[[], Screen]
    ) -> None:
        """Adds a mode and its corresponding base screen to the app.

        Args:
            mode: The new mode.
            base_screen: The base screen associated with the given mode.

        Raises:
            InvalidModeError: If the name of the mode is not valid/duplicated.
        """
        if mode == "_default":
            raise InvalidModeError("Cannot use '_default' as a custom mode.")
        elif mode in self.MODES:
            raise InvalidModeError(f"Duplicated mode name {mode!r}.")

        self.MODES[mode] = base_screen

    def remove_mode(self, mode: str) -> None:
        """Removes a mode from the app.

        Screens that are running in the stack of that mode are scheduled for pruning.

        Args:
            mode: The mode to remove. It can't be the active mode.

        Raises:
            ActiveModeError: If trying to remove the active mode.
            UnknownModeError: If trying to remove an unknown mode.
        """
        if mode == self._current_mode:
            raise ActiveModeError(f"Can't remove active mode {mode!r}")
        elif mode not in self.MODES:
            raise UnknownModeError(f"Unknown mode {mode!r}")
        else:
            del self.MODES[mode]

        if mode not in self._screen_stacks:
            return

        stack = self._screen_stacks[mode]
        del self._screen_stacks[mode]
        for screen in reversed(stack):
            self._replace_screen(screen)

    def is_screen_installed(self, screen: Screen | str) -> bool:
        """Check if a given screen has been installed.

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).

        Returns:
            True if the screen is currently installed,
        """
        if isinstance(screen, str):
            return screen in self._installed_screens
        else:
            return screen in self._installed_screens.values()

    def get_screen(self, screen: Screen | str) -> Screen:
        """Get an installed screen.

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).

        Raises:
            KeyError: If the named screen doesn't exist.

        Returns:
            A screen instance.
        """
        if isinstance(screen, str):
            try:
                next_screen = self._installed_screens[screen]
            except KeyError:
                raise KeyError(f"No screen called {screen!r} installed") from None
            if callable(next_screen):
                next_screen = next_screen()
                self._installed_screens[screen] = next_screen
        else:
            next_screen = screen
        return next_screen

    def _get_screen(self, screen: Screen | str) -> tuple[Screen, AwaitMount]:
        """Get an installed screen and an AwaitMount object.

        If the screen isn't running, it will be registered before it is run.

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).

        Raises:
            KeyError: If the named screen doesn't exist.

        Returns:
            A screen instance and an awaitable that awaits the children mounting.
        """
        _screen = self.get_screen(screen)
        if not _screen.is_running:
            widgets = self._register(self, _screen)
            await_mount = AwaitMount(_screen, widgets)
            self.call_next(await_mount)
            return (_screen, await_mount)
        else:
            await_mount = AwaitMount(_screen, [])
            self.call_next(await_mount)
            return (_screen, await_mount)

    def _load_screen_css(self, screen: Screen):
        """Loads the CSS associated with a screen."""

        if self.css_monitor is not None:
            self.css_monitor.add_paths(screen.css_path)

        update = False
        for path in screen.css_path:
            if not self.stylesheet.has_source(path):
                self.stylesheet.read(path)
                update = True
        if screen.CSS:
            try:
                screen_css_path = (
                    f"{inspect.getfile(screen.__class__)}:{screen.__class__.__name__}"
                )
            except (TypeError, OSError):
                screen_css_path = f"{screen.__class__.__name__}"
            if not self.stylesheet.has_source(screen_css_path):
                self.stylesheet.add_source(
                    screen.CSS,
                    path=screen_css_path,
                    is_default_css=False,
                    scope=screen._css_type_name if screen.SCOPED_CSS else "",
                )
                update = True
        if update:
            self.stylesheet.reparse()
            self.stylesheet.update(self)

    def _replace_screen(self, screen: Screen) -> Screen:
        """Handle the replaced screen.

        Args:
            screen: A screen object.

        Returns:
            The screen that was replaced.
        """
        if self._screen_stack:
            self.screen.refresh()
        screen.post_message(events.ScreenSuspend())
        self.log.system(f"{screen} SUSPENDED")
        if not self.is_screen_installed(screen) and all(
            screen not in stack for stack in self._screen_stacks.values()
        ):
            screen.remove()
            self.log.system(f"{screen} REMOVED")
        return screen

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[False] = False,
    ) -> AwaitMount:
        ...

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[True] = True,
    ) -> asyncio.Future[ScreenResultType]:
        ...

    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: bool = False,
    ) -> AwaitMount | asyncio.Future[ScreenResultType]:
        """Push a new [screen](/guide/screens) on the screen stack, making it the current screen.

        Args:
            screen: A Screen instance or the name of an installed screen.
            callback: An optional callback function that will be called if the screen is [dismissed][textual.screen.Screen.dismiss] with a result.
            wait_for_dismiss: If `True`, awaiting this method will return the dismiss value from the screen. When set to `False`, awaiting
                this method will wait for the screen to be mounted. Note that `wait_for_dismiss` should only be set to `True` when running in a worker.

        Raises:
            NoActiveWorker: If using `wait_for_dismiss` outside of a worker.

        Returns:
            An optional awaitable that awaits the mounting of the screen and its children, or an asyncio Future
                to await the result of the screen.
        """
        if not isinstance(screen, (Screen, str)):
            raise TypeError(
                f"push_screen requires a Screen instance or str; not {screen!r}"
            )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Mainly for testing, when push_screen isn't called in an async context
            future: asyncio.Future[ScreenResultType] = asyncio.Future()
        else:
            future = loop.create_future()

        if self._screen_stack:
            self.screen.post_message(events.ScreenSuspend())
            self.screen.refresh()
        next_screen, await_mount = self._get_screen(screen)
        try:
            message_pump = active_message_pump.get()
        except LookupError:
            message_pump = self.app

        next_screen._push_result_callback(message_pump, callback, future)
        self._load_screen_css(next_screen)
        self._screen_stack.append(next_screen)
        self.stylesheet.update(next_screen)
        next_screen.post_message(events.ScreenResume())
        self.log.system(f"{self.screen} is current (PUSHED)")
        if wait_for_dismiss:
            try:
                get_current_worker()
            except NoActiveWorker:
                raise NoActiveWorker(
                    "push_screen must be run from a worker when `wait_for_dismiss` is True"
                ) from None
            return future
        else:
            return await_mount

    def switch_screen(self, screen: Screen | str) -> AwaitMount:
        """Switch to another [screen](/guide/screens) by replacing the top of the screen stack with a new screen.

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).
        """
        if not isinstance(screen, (Screen, str)):
            raise TypeError(
                f"switch_screen requires a Screen instance or str; not {screen!r}"
            )

        next_screen, await_mount = self._get_screen(screen)
        if screen is self.screen or next_screen is self.screen:
            self.log.system(f"Screen {screen} is already current.")
            return AwaitMount(self.screen, [])

        previous_screen = self._replace_screen(self._screen_stack.pop())
        previous_screen._pop_result_callback()
        self._load_screen_css(next_screen)
        self._screen_stack.append(next_screen)
        self.screen.post_message(events.ScreenResume())
        self.screen._push_result_callback(self.screen, None)
        self.log.system(f"{self.screen} is current (SWITCHED)")
        return await_mount

    def install_screen(self, screen: Screen, name: str) -> None:
        """Install a screen.

        Installing a screen prevents Textual from destroying it when it is no longer on the screen stack.
        Note that you don't need to install a screen to use it. See [push_screen][textual.app.App.push_screen]
        or [switch_screen][textual.app.App.switch_screen] to make a new screen current.

        Args:
            screen: Screen to install.
            name: Unique name to identify the screen.

        Raises:
            ScreenError: If the screen can't be installed.

        Returns:
            An awaitable that awaits the mounting of the screen and its children.
        """
        if name in self._installed_screens:
            raise ScreenError(f"Can't install screen; {name!r} is already installed")
        if screen in self._installed_screens.values():
            raise ScreenError(
                "Can't install screen; {screen!r} has already been installed"
            )
        self._installed_screens[name] = screen
        self.log.system(f"{screen} INSTALLED name={name!r}")

    def uninstall_screen(self, screen: Screen | str) -> str | None:
        """Uninstall a screen.

        If the screen was not previously installed then this method is a null-op.
        Uninstalling a screen allows Textual to delete it when it is popped or switched.
        Note that uninstalling a screen is only required if you have previously installed it
        with [install_screen][textual.app.App.install_screen].
        Textual will also uninstall screens automatically on exit.

        Args:
            screen: The screen to uninstall or the name of a installed screen.

        Returns:
            The name of the screen that was uninstalled, or None if no screen was uninstalled.
        """
        if isinstance(screen, str):
            if screen not in self._installed_screens:
                return None
            uninstall_screen = self._installed_screens[screen]
            if any(uninstall_screen in stack for stack in self._screen_stacks.values()):
                raise ScreenStackError("Can't uninstall screen in screen stack")
            del self._installed_screens[screen]
            self.log.system(f"{uninstall_screen} UNINSTALLED name={screen!r}")
            return screen
        else:
            if any(screen in stack for stack in self._screen_stacks.values()):
                raise ScreenStackError("Can't uninstall screen in screen stack")
            for name, installed_screen in self._installed_screens.items():
                if installed_screen is screen:
                    self._installed_screens.pop(name)
                    self.log.system(f"{screen} UNINSTALLED name={name!r}")
                    return name
        return None

    def pop_screen(self) -> Screen[object]:
        """Pop the current [screen](/guide/screens) from the stack, and switch to the previous screen.

        Returns:
            The screen that was replaced.
        """
        screen_stack = self._screen_stack
        if len(screen_stack) <= 1:
            raise ScreenStackError(
                "Can't pop screen; there must be at least one screen on the stack"
            )
        previous_screen = self._replace_screen(screen_stack.pop())
        previous_screen._pop_result_callback()
        self.screen.post_message(events.ScreenResume())
        self.log.system(f"{self.screen} is active")
        return previous_screen

    def set_focus(self, widget: Widget | None, scroll_visible: bool = True) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget: Widget to focus.
            scroll_visible: Scroll widget in to view.
        """
        self.screen.set_focus(widget, scroll_visible)

    def _set_mouse_over(self, widget: Widget | None) -> None:
        """Called when the mouse is over another widget.

        Args:
            widget: Widget under mouse, or None for no widgets.
        """
        if widget is None:
            if self.mouse_over is not None:
                try:
                    self.mouse_over.post_message(events.Leave())
                finally:
                    self.mouse_over = None
        else:
            if self.mouse_over is not widget:
                try:
                    if self.mouse_over is not None:
                        self.mouse_over.post_message(events.Leave())
                    if widget is not None:
                        widget.post_message(events.Enter())
                finally:
                    self.mouse_over = widget

    def capture_mouse(self, widget: Widget | None) -> None:
        """Send all mouse events to the given widget or disable mouse capture.

        Args:
            widget: If a widget, capture mouse event, or `None` to end mouse capture.
        """
        if widget == self.mouse_captured:
            return
        if self.mouse_captured is not None:
            self.mouse_captured.post_message(events.MouseRelease(self.mouse_position))
        self.mouse_captured = widget
        if widget is not None:
            widget.post_message(events.MouseCapture(self.mouse_position))

    def panic(self, *renderables: RenderableType) -> None:
        """Exits the app and display error message(s).

        Used in response to unexpected errors.
        For a more graceful exit, see the [exit][textual.app.App.exit] method.

        Args:
            *renderables: Text or Rich renderable(s) to display on exit.
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

        Always results in the app exiting.

        Args:
            error: An exception instance.
        """
        self._return_code = 1
        # If we're running via pilot and this is the first exception encountered,
        # take note of it so that we can re-raise for test frameworks later.
        if self.is_headless and self._exception is None:
            self._exception = error
            self._exception_event.set()

        if hasattr(error, "__rich__"):
            # Exception has a rich method, so we can defer to that for the rendering
            self.panic(error)
        else:
            # Use default exception rendering
            self._fatal_error()

    def _fatal_error(self) -> None:
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
        """Print and clear exit renderables."""
        error_count = len(self._exit_renderables)
        if "debug" in self.features:
            for renderable in self._exit_renderables:
                self.error_console.print(renderable)
            if error_count > 1:
                self.error_console.print(
                    f"\n[b]NOTE:[/b] {error_count} errors shown above.", markup=True
                )
        elif self._exit_renderables:
            self.error_console.print(self._exit_renderables[0])
            if error_count > 1:
                self.error_console.print(
                    f"\n[b]NOTE:[/b] 1 of {error_count} errors shown. Run with [b]textual run --dev[/] to see all errors.",
                    markup=True,
                )

        self._exit_renderables.clear()

    async def _process_messages(
        self,
        ready_callback: CallbackType | None = None,
        headless: bool = False,
        terminal_size: tuple[int, int] | None = None,
        message_hook: Callable[[Message], None] | None = None,
    ) -> None:
        self._set_active()
        active_message_pump.set(self)

        if self.devtools is not None:
            from textual_dev.client import DevtoolsConnectionError

            try:
                await self.devtools.connect()
                self.log.system(f"Connected to devtools ( {self.devtools.url} )")
            except DevtoolsConnectionError:
                self.log.system(f"Couldn't connect to devtools ( {self.devtools.url} )")

        self.log.system("---")

        self.log.system(driver=self.driver_class)
        self.log.system(loop=asyncio.get_running_loop())
        self.log.system(features=self.features)
        if constants.LOG_FILE is not None:
            _log_path = os.path.abspath(constants.LOG_FILE)
            self.log.system(f"Writing logs to {_log_path!r}")

        try:
            if self.css_path:
                self.stylesheet.read_all(self.css_path)
            for path, css, tie_breaker, scope in self._get_default_css():
                self.stylesheet.add_source(
                    css,
                    path=path,
                    is_default_css=True,
                    tie_breaker=tie_breaker,
                    scope=scope,
                )
            if self.CSS:
                try:
                    app_css_path = (
                        f"{inspect.getfile(self.__class__)}:{self.__class__.__name__}"
                    )
                except (TypeError, OSError):
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
            self.log.system("STARTED", self.css_monitor)

        async def run_process_messages():
            """The main message loop, invoke below."""

            async def invoke_ready_callback() -> None:
                if ready_callback is not None:
                    ready_result = ready_callback()
                    if inspect.isawaitable(ready_result):
                        await ready_result

            with self.batch_update():
                try:
                    try:
                        await self._dispatch_message(events.Compose())
                        default_screen = self.screen
                        await self._dispatch_message(events.Mount())
                        self.check_idle()
                    finally:
                        self._mounted_event.set()

                    Reactive._initialize_object(self)

                    self.stylesheet.update(self)
                    if self.screen is not default_screen:
                        self.stylesheet.update(default_screen)

                    await self.animator.start()

                except Exception:
                    await self.animator.stop()
                    raise

                finally:
                    self._running = True
                    await self._ready()
                    await invoke_ready_callback()

            try:
                await self._process_messages_loop()
            except asyncio.CancelledError:
                pass
            finally:
                self.workers.cancel_all()
                self._running = False
                try:
                    await self.animator.stop()
                finally:
                    for timer in list(self._timers):
                        timer.stop()

        self._running = True
        try:
            load_event = events.Load()
            await self._dispatch_message(load_event)

            driver: Driver
            driver_class = cast(
                "type[Driver]",
                HeadlessDriver if headless else self.driver_class,
            )
            driver = self._driver = driver_class(
                self,
                debug=constants.DEBUG,
                size=terminal_size,
            )

            if not self._exit:
                driver.start_application_mode()
                try:
                    with redirect_stdout(self._capture_stdout):
                        with redirect_stderr(self._capture_stderr):
                            await run_process_messages()

                finally:
                    driver.stop_application_mode()
        except Exception as error:
            self._handle_exception(error)

    async def _pre_process(self) -> bool:
        """Special case for the app, which doesn't need the functionality in MessagePump."""
        return True

    async def _ready(self) -> None:
        """Called immediately prior to processing messages.

        May be used as a hook for any operations that should run first.
        """

        ready_time = (perf_counter() - self._start_time) * 1000
        self.log.info(f"ready in {ready_time:0.0f} milliseconds")

        async def take_screenshot() -> None:
            """Take a screenshot and exit."""
            self.save_screenshot()
            self.exit()

        if constants.SCREENSHOT_DELAY >= 0:
            self.set_timer(
                constants.SCREENSHOT_DELAY, take_screenshot, name="screenshot timer"
            )

    async def _on_compose(self) -> None:
        try:
            widgets = [*self.screen._nodes, *compose(self)]
        except TypeError as error:
            raise TypeError(
                f"{self!r} compose() method returned an invalid result; {error}"
            ) from error

        await self.mount_all(widgets)

    def _on_idle(self) -> None:
        """Perform actions when there are no messages in the queue."""

    def _register_child(
        self, parent: DOMNode, child: Widget, before: int | None, after: int | None
    ) -> None:
        """Register a widget as a child of another.

        Args:
            parent: Parent node.
            child: The child widget to register.
            widgets: The widget to register.
            before: A location to mount before.
            after: A location to mount after.
        """

        # Let's be 100% sure that we've not been asked to do a before and an
        # after at the same time. It's possible that we can remove this
        # check later on, but for the purposes of development right now,
        # it's likely a good idea to keep it here to check assumptions in
        # the rest of the code.
        if before is not None and after is not None:
            raise AppError("Only one of 'before' and 'after' may be specified.")

        # If we don't already know about this widget...
        if child not in self._registry:
            # Now to figure out where to place it. If we've got a `before`...
            if before is not None:
                # ...it's safe to NodeList._insert before that location.
                parent._nodes._insert(before, child)
            elif after is not None and after != -1:
                # In this case we've got an after. -1 holds the special
                # position (for now) of meaning "okay really what I mean is
                # do an append, like if I'd asked to add with no before or
                # after". So... we insert before the next item in the node
                # list, iff after isn't -1.
                parent._nodes._insert(after + 1, child)
            else:
                # At this point we appear to not be adding before or after,
                # or we've got a before/after value that really means
                # "please append". So...
                parent._nodes._append(child)

            # Now that the widget is in the NodeList of its parent, sort out
            # the rest of the admin.
            self._registry.add(child)
            child._attach(parent)
            child._post_register(self)
            child._start_messages()

    def _register(
        self,
        parent: DOMNode,
        *widgets: Widget,
        before: int | None = None,
        after: int | None = None,
    ) -> list[Widget]:
        """Register widget(s) so they may receive events.

        Args:
            parent: Parent node.
            *widgets: The widget(s) to register.
            before: A location to mount before.
            after: A location to mount after.

        Returns:
            List of modified widgets.
        """

        if not widgets:
            return []

        widget_list: Iterable[Widget]
        if before is not None or after is not None:
            # There's a before or after, which means there's going to be an
            # insertion, so make it easier to get the new things in the
            # correct order.
            widget_list = reversed(widgets)
        else:
            widget_list = widgets

        apply_stylesheet = self.stylesheet.apply
        for widget in widget_list:
            if not isinstance(widget, Widget):
                raise AppError(f"Can't register {widget!r}; expected a Widget instance")
            if widget not in self._registry:
                self._register_child(parent, widget, before, after)
                if widget._nodes:
                    self._register(widget, *widget._nodes)
                apply_stylesheet(widget)

        if not self._running:
            # If the app is not running, prevent awaiting of the widget tasks
            return []

        return list(widgets)

    def _unregister(self, widget: Widget) -> None:
        """Unregister a widget.

        Args:
            widget: A Widget to unregister
        """
        widget.blur()
        if isinstance(widget._parent, Widget):
            widget._parent._nodes._remove(widget)
            widget._detach()
        self._registry.discard(widget)

    async def _disconnect_devtools(self):
        if self.devtools is not None:
            await self.devtools.disconnect()

    def _start_widget(self, parent: Widget, widget: Widget) -> None:
        """Start a widget (run it's task) so that it can receive messages.

        Args:
            parent: The parent of the Widget.
            widget: The Widget to start.
        """

        widget._attach(parent)
        widget._start_messages()
        self.app._registry.add(widget)

    def is_mounted(self, widget: Widget) -> bool:
        """Check if a widget is mounted.

        Args:
            widget: A widget.

        Returns:
            True of the widget is mounted.
        """
        return widget in self._registry

    async def _close_all(self) -> None:
        """Close all message pumps."""

        # Close all screens on all stacks:
        for stack in self._screen_stacks.values():
            for stack_screen in reversed(stack):
                if stack_screen._running:
                    await self._prune_node(stack_screen)
            stack.clear()

        # Close pre-defined screens.
        for screen in self.SCREENS.values():
            if isinstance(screen, Screen) and screen._running:
                await self._prune_node(screen)

        # Close any remaining nodes
        # Should be empty by now
        remaining_nodes = list(self._registry)
        for child in remaining_nodes:
            await child._close_messages()

    async def _shutdown(self) -> None:
        self._begin_batch()  # Prevents any layout / repaint while shutting down
        driver = self._driver
        self._running = False
        if driver is not None:
            driver.disable_input()
        await self._close_all()
        await self._close_messages()

        await self._dispatch_message(events.Unmount())

        if self._driver is not None:
            self._driver.close()

        if self.devtools is not None and self.devtools.is_connected:
            await self._disconnect_devtools()

        self._print_error_renderables()

        if constants.SHOW_RETURN:
            from rich.console import Console
            from rich.pretty import Pretty

            console = Console()
            console.print("[b]The app returned:")
            console.print(Pretty(self._return_value))

    async def _on_exit_app(self) -> None:
        self._begin_batch()  # Prevent repaint / layout while shutting down
        await self._message_queue.put(None)

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> None:
        if self._screen_stack:
            self.screen.refresh(repaint=repaint, layout=layout)
        self.check_idle()

    def refresh_css(self, animate: bool = True) -> None:
        """Refresh CSS.

        Args:
            animate: Also execute CSS animations.
        """
        stylesheet = self.app.stylesheet
        stylesheet.set_variables(self.get_css_variables())
        stylesheet.reparse()
        stylesheet.update(self.app, animate=animate)
        self.screen._refresh_layout(self.size, full=True)
        # The other screens in the stack will need to know about some style
        # changes, as a final pass let's check in on every screen that isn't
        # the current one and update them too.
        for screen in self.screen_stack:
            if screen != self.screen:
                stylesheet.update(screen, animate=animate)

    def _display(self, screen: Screen, renderable: RenderableType | None) -> None:
        """Display a renderable within a sync.

        Args:
            screen: Screen instance
            renderable: A Rich renderable.
        """

        try:
            if renderable is None:
                return

            if (
                self._running
                and not self._closed
                and not self.is_headless
                and self._driver is not None
            ):
                console = self.console
                self._begin_update()
                try:
                    try:
                        if isinstance(renderable, CompositorUpdate):
                            cursor_x, cursor_y = self.cursor_position
                            terminal_sequence = renderable.render_segments(console)
                            terminal_sequence += Control.move_to(
                                cursor_x, cursor_y
                            ).segment.text
                        else:
                            segments = console.render(renderable)
                            terminal_sequence = console._render_buffer(segments)
                    except Exception as error:
                        self._handle_exception(error)
                    else:
                        self._driver.write(terminal_sequence)
                finally:
                    self._end_update()

                self._driver.flush()

        finally:
            self.post_display_hook()

    def post_display_hook(self) -> None:
        """Called immediately after a display is done. Used in tests."""

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        """Get the widget under the given coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            The widget and the widget's screen region.
        """
        return self.screen.get_widget_at(x, y)

    def bell(self) -> None:
        """Play the console 'bell'.

        For terminals that support a bell, this typically makes a notification or error sound.
        Some terminals may make no sound or display a visual bell indicator, depending on configuration.
        """
        if not self.is_headless and self._driver is not None:
            self._driver.write("\07")

    @property
    def _binding_chain(self) -> list[tuple[DOMNode, _Bindings]]:
        """Get a chain of nodes and bindings to consider.

        If no widget is focused, returns the bindings from both the screen and the app level bindings.
        Otherwise, combines all the bindings from the currently focused node up the DOM to the root App.
        """
        focused = self.focused
        namespace_bindings: list[tuple[DOMNode, _Bindings]]

        if focused is None:
            namespace_bindings = [
                (self.screen, self.screen._bindings),
                (self, self._bindings),
            ]
        else:
            namespace_bindings = [
                (node, node._bindings) for node in focused.ancestors_with_self
            ]

        return namespace_bindings

    @property
    def _modal_binding_chain(self) -> list[tuple[DOMNode, _Bindings]]:
        """The binding chain, ignoring everything before the last modal."""
        binding_chain = self._binding_chain
        for index, (node, _bindings) in enumerate(binding_chain, 1):
            if node.is_modal:
                return binding_chain[:index]
        return binding_chain

    async def check_bindings(self, key: str, priority: bool = False) -> bool:
        """Handle a key press.

        This method is used internally by the bindings system, but may be called directly
        if you wish to *simulate* a key being pressed.

        Args:
            key: A key.
            priority: If `True` check from `App` down, otherwise from focused up.

        Returns:
            True if the key was handled by a binding, otherwise False
        """
        for namespace, bindings in (
            reversed(self._binding_chain) if priority else self._modal_binding_chain
        ):
            binding = bindings.keys.get(key)
            if binding is not None and binding.priority == priority:
                if await self.run_action(binding.action, namespace):
                    return True
        return False

    async def on_event(self, event: events.Event) -> None:
        # Handle input events that haven't been forwarded
        # If the event has been forwarded it may have bubbled up back to the App
        if isinstance(event, events.Compose):
            screen = Screen(id=f"_default")
            self._register(self, screen)
            self._screen_stack.append(screen)
            screen.post_message(events.ScreenResume())
            await super().on_event(event)

        elif isinstance(event, events.InputEvent) and not event.is_forwarded:
            if isinstance(event, events.MouseEvent):
                # Record current mouse position on App
                self.mouse_position = Offset(event.x, event.y)
                self.screen._forward_event(event)
            elif isinstance(event, events.Key):
                if not await self.check_bindings(event.key, priority=True):
                    forward_target = self.focused or self.screen
                    forward_target._forward_event(event)
            else:
                self.screen._forward_event(event)

        elif isinstance(event, events.Paste) and not event.is_forwarded:
            if self.focused is not None:
                self.focused._forward_event(event)
            else:
                self.screen._forward_event(event)
        else:
            await super().on_event(event)

    async def run_action(
        self,
        action: str | ActionParseResult,
        default_namespace: object | None = None,
    ) -> bool:
        """Perform an [action](/guide/actions).

        Actions are typically associated with key bindings, where you wouldn't need to call this method manually.

        Args:
            action: Action encoded in a string.
            default_namespace: Namespace to use if not provided in the action,
                or None to use app.

        Returns:
            True if the event has been handled.
        """
        if isinstance(action, str):
            target, params = actions.parse(action)
        else:
            target, params = action
        implicit_destination = True
        if "." in target:
            destination, action_name = target.split(".", 1)
            if destination not in self._action_targets:
                raise ActionError(f"Action namespace {destination} is not known")
            action_target = getattr(self, destination)
            implicit_destination = True
        else:
            action_target = default_namespace if default_namespace is not None else self
            action_name = target

        handled = await self._dispatch_action(action_target, action_name, params)
        if not handled and implicit_destination and not isinstance(action_target, App):
            handled = await self.app._dispatch_action(self.app, action_name, params)
        return handled

    async def _dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> bool:
        """Dispatch an action to an action method.

        Args:
            namespace: Namespace (object) of action.
            action_name: Name of the action.
            params: Action parameters.

        Returns:
            True if handled, otherwise False.
        """
        _rich_traceback_guard = True

        log(
            "<action>",
            namespace=namespace,
            action_name=action_name,
            params=params,
        )

        try:
            private_method = getattr(namespace, f"_action_{action_name}", None)
            if callable(private_method):
                await invoke(private_method, *params)
                return True
            public_method = getattr(namespace, f"action_{action_name}", None)
            if callable(public_method):
                await invoke(public_method, *params)
                return True
            log(
                f"<action> {action_name!r} has no target."
                f" Could not find methods '_action_{action_name}' or 'action_{action_name}'"
            )
        except SkipAction:
            # The action method raised this to explicitly not handle the action
            log(f"<action> {action_name!r} skipped.")
        return False

    async def _broker_event(
        self, event_name: str, event: events.Event, default_namespace: object | None
    ) -> bool:
        """Allow the app an opportunity to dispatch events to action system.

        Args:
            event_name: _description_
            event: An event object.
            default_namespace: The default namespace, where one isn't supplied.

        Returns:
            True if an action was processed.
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
            await self.run_action(action, default_namespace=default_namespace)  # type: ignore[arg-type]
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
        if not (await self.check_bindings(event.key)):
            await self.dispatch_key(event)

    async def _on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log("shutdown request")
        await self._close_messages()

    async def _on_resize(self, event: events.Resize) -> None:
        event.stop()
        self.screen.post_message(event)
        for screen in self._background_screens:
            screen.post_message(event)

    def _detach_from_dom(self, widgets: list[Widget]) -> list[Widget]:
        """Detach a list of widgets from the DOM.

        Args:
            widgets: The list of widgets to detach from the DOM.

        Returns:
            The list of widgets that should be pruned.

        Note:
            A side-effect of calling this function is that each parent of
            each affected widget will be made to forget about the affected
            child.
        """

        # We've been given a list of widgets to remove, but removing those
        # will also result in other (descendent) widgets being removed. So
        # to start with let's get a list of everything that's not going to
        # be in the DOM by the time we've finished. Note that, at this
        # point, it's entirely possible that there will be duplicates.
        everything_to_remove: list[Widget] = []
        for widget in widgets:
            everything_to_remove.extend(
                widget.walk_children(
                    Widget, with_self=True, method="depth", reverse=True
                )
            )

        # Next up, let's quickly create a deduped collection of things to
        # remove and ensure that, if one of them is the focused widget,
        # focus gets moved to somewhere else.
        dedupe_to_remove = set(everything_to_remove)
        if self.screen.focused in dedupe_to_remove:
            self.screen._reset_focus(
                self.screen.focused,
                [to_remove for to_remove in dedupe_to_remove if to_remove.can_focus],
            )

        # Next, we go through the set of widgets we've been asked to remove
        # and try and find the minimal collection of widgets that will
        # result in everything else that should be removed, being removed.
        # In other words: find the smallest set of ancestors in the DOM that
        # will remove the widgets requested for removal, and also ensure
        # that all knock-on effects happen too.
        request_remove = set(widgets)
        pruned_remove = [
            widget for widget in widgets if request_remove.isdisjoint(widget.ancestors)
        ]

        # Now that we know that minimal set of widgets, we go through them
        # and get their parents to forget about them. This has the effect of
        # snipping each affected branch from the DOM.
        for widget in pruned_remove:
            if widget.parent is not None:
                widget.parent._nodes._remove(widget)

        for node in pruned_remove:
            node._detach()

        # Return the list of widgets that should end up being sent off in a
        # prune event.
        return pruned_remove

    def _walk_children(self, root: Widget) -> Iterable[list[Widget]]:
        """Walk children depth first, generating widgets and a list of their siblings.

        Returns:
            The child widgets of root.
        """
        stack: list[Widget] = [root]
        pop = stack.pop
        push = stack.append

        while stack:
            widget = pop()
            children = [*widget._nodes, *widget._get_virtual_dom()]
            if children:
                yield children
            for child in widget._nodes:
                push(child)

    def _remove_nodes(
        self, widgets: list[Widget], parent: DOMNode | None
    ) -> AwaitRemove:
        """Remove nodes from DOM, and return an awaitable that awaits cleanup.

        Args:
            widgets: List of nodes to remove.
            parent: Parent node of widgets, or None for no parent.

        Returns:
            Awaitable that returns when the nodes have been fully removed.
        """

        async def prune_widgets_task(
            widgets: list[Widget], finished_event: asyncio.Event
        ) -> None:
            """Prune widgets as a background task.

            Args:
                widgets: Widgets to prune.
                finished_event: Event to set when complete.
            """
            try:
                await self._prune_nodes(widgets)
            finally:
                finished_event.set()
                if parent is not None:
                    parent.refresh(layout=True)

        removed_widgets = self._detach_from_dom(widgets)

        finished_event = asyncio.Event()
        remove_task = create_task(
            prune_widgets_task(removed_widgets, finished_event), name="prune nodes"
        )

        await_remove = AwaitRemove(finished_event, remove_task)
        self.call_next(await_remove)
        return await_remove

    async def _prune_nodes(self, widgets: list[Widget]) -> None:
        """Remove nodes and children.

        Args:
            widgets: Widgets to remove.
        """
        async with self._dom_lock:
            for widget in widgets:
                await self._prune_node(widget)

    async def _prune_node(self, root: Widget) -> None:
        """Remove a node and its children. Children are removed before parents.

        Args:
            root: Node to remove.
        """
        # Pruning a node that has been removed is a no-op
        if root not in self._registry:
            return

        node_children = list(self._walk_children(root))

        for children in reversed(node_children):
            # Closing children can be done asynchronously.
            close_messages = [
                child._close_messages(wait=True) for child in children if child._running
            ]
            # TODO: What if a message pump refuses to exit?
            if close_messages:
                await asyncio.gather(*close_messages)
                for child in children:
                    self._unregister(child)

        await root._close_messages(wait=True)
        self._unregister(root)

    async def action_check_bindings(self, key: str) -> None:
        """An [action](/guide/actions) to handle a key press using the binding system.

        Args:
            key: The key to process.
        """
        if not await self.check_bindings(key, priority=True):
            await self.check_bindings(key, priority=False)

    async def action_quit(self) -> None:
        """An [action](/guide/actions) to quit the app as soon as possible."""
        self.exit()

    async def action_bell(self) -> None:
        """An [action](/guide/actions) to play the terminal 'bell'."""
        self.bell()

    async def action_focus(self, widget_id: str) -> None:
        """An [action](/guide/actions) to focus the given widget.

        Args:
            widget_id: ID of widget to focus.
        """
        try:
            node = self.query(f"#{widget_id}").first()
        except NoMatches:
            pass
        else:
            if isinstance(node, Widget):
                self.set_focus(node)

    async def action_switch_screen(self, screen: str) -> None:
        """An [action](/guide/actions) to switch screens.

        Args:
            screen: Name of the screen.
        """
        self.switch_screen(screen)

    async def action_push_screen(self, screen: str) -> None:
        """An [action](/guide/actions) to push a new screen on to the stack and make it active.

        Args:
            screen: Name of the screen.
        """
        self.push_screen(screen)

    async def action_pop_screen(self) -> None:
        """An [action](/guide/actions) to remove the topmost screen and makes the new topmost screen active."""
        self.pop_screen()

    async def action_switch_mode(self, mode: str) -> None:
        """An [action](/guide/actions) that switches to the given mode.."""
        self.switch_mode(mode)

    async def action_back(self) -> None:
        """An [action](/guide/actions) to go back to the previous screen (pop the current screen).

        Note:
            If there is no screen to go back to, this is a non-operation (in
            other words it's safe to call even if there are no other screens
            on the stack.)
        """
        try:
            self.pop_screen()
        except ScreenStackError:
            pass

    async def action_add_class(self, selector: str, class_name: str) -> None:
        """An [action](/guide/actions) to add a CSS class to the selected widget.

        Args:
            selector: Selects the widget to add the class to.
            class_name: The class to add to the selected widget.
        """
        self.screen.query(selector).add_class(class_name)

    async def action_remove_class(self, selector: str, class_name: str) -> None:
        """An [action](/guide/actions) to remove a CSS class from the selected widget.

        Args:
            selector: Selects the widget to remove the class from.
            class_name: The class to remove from  the selected widget."""
        self.screen.query(selector).remove_class(class_name)

    async def action_toggle_class(self, selector: str, class_name: str) -> None:
        """An [action](/guide/actions) to toggle a CSS class on the selected widget.

        Args:
            selector: Selects the widget to toggle the class on.
            class_name: The class to toggle on the selected widget.
        """
        self.screen.query(selector).toggle_class(class_name)

    def action_focus_next(self) -> None:
        """An [action](/guide/actions) to focus the next widget."""
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        """An [action](/guide/actions) to focus the previous widget."""
        self.screen.focus_previous()

    def _on_terminal_supports_synchronized_output(
        self, message: messages.TerminalSupportsSynchronizedOutput
    ) -> None:
        log.system("SynchronizedOutput mode is supported")
        self._sync_available = True

    def _begin_update(self) -> None:
        if self._sync_available and self._driver is not None:
            self._driver.write(SYNC_START)

    def _end_update(self) -> None:
        if self._sync_available and self._driver is not None:
            self._driver.write(SYNC_END)

    def _refresh_notifications(self) -> None:
        """Refresh the notifications on the current screen, if one is available."""
        # If we've got a screen to hand...
        try:
            screen = self.screen
        except ScreenStackError:
            pass
        else:
            try:
                # ...see if it has a toast rack.
                toast_rack = screen.get_child_by_type(ToastRack)
            except NoMatches:
                # It doesn't. That's fine. Either there won't ever be one,
                # or one will turn up. Things will work out later.
                return
            # Update the toast rack.
            toast_rack.show(self._notifications)

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float = Notification.timeout,
    ) -> None:
        """Create a notification.

        !!! tip

            This method is thread-safe.


        Args:
            message: The message for the notification.
            title: The title for the notification.
            severity: The severity of the notification.
            timeout: The timeout for the notification.

        The `notify` method is used to create an application-wide
        notification, shown in a [`Toast`][textual.widgets._toast.Toast],
        normally originating in the bottom right corner of the display.

        Notifications can have the following severity levels:

        - `information`
        - `warning`
        - `error`

        The default is `information`.

        Example:
            ```python
            # Show an information notification.
            self.notify("It's an older code, sir, but it checks out.")

            # Show a warning. Note that Textual's notification system allows
            # for the use of Rich console markup.
            self.notify(
                "Now witness the firepower of this fully "
                "[b]ARMED[/b] and [i][b]OPERATIONAL[/b][/i] battle station!",
                title="Possible trap detected",
                severity="warning",
            )

            # Show an error. Set a longer timeout so it's noticed.
            self.notify("It's a trap!", severity="error", timeout=10)

            # Show an information notification, but without any sort of title.
            self.notify("It's against my programming to impersonate a deity.", title="")
            ```
        """
        notification = Notification(message, title, severity, timeout)
        self.post_message(Notify(notification))

    def _on_notify(self, event: Notify) -> None:
        """Handle notification message."""
        self._notifications.add(event.notification)
        self._refresh_notifications()

    def _unnotify(self, notification: Notification, refresh: bool = True) -> None:
        """Remove a notification from the notification collection.

        Args:
            notification: The notification to remove.
            refresh: Flag to say if the display of notifications should be refreshed.
        """
        del self._notifications[notification]
        if refresh:
            self._refresh_notifications()

    def clear_notifications(self) -> None:
        """Clear all the current notifications."""
        self._notifications.clear()
        self._refresh_notifications()

    def action_command_palette(self) -> None:
        """Show the Textual command palette."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            self.push_screen(CommandPalette(), callback=self.call_next)
