"""

Here you will find the [App][textual.app.App] class, which is the base class for Textual apps.

See [app basics](/guide/app) for how to build Textual apps.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import io
import mimetypes
import os
import signal
import sys
import threading
import uuid
import warnings
from asyncio import AbstractEventLoop, Task, create_task
from concurrent.futures import Future
from contextlib import (
    asynccontextmanager,
    contextmanager,
    redirect_stderr,
    redirect_stdout,
)
from functools import partial
from pathlib import Path
from time import perf_counter
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    BinaryIO,
    Callable,
    ClassVar,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    NamedTuple,
    Sequence,
    TextIO,
    Type,
    TypeVar,
    overload,
)
from weakref import WeakKeyDictionary, WeakSet

import rich
import rich.repr
from platformdirs import user_downloads_path
from rich.console import Console, ConsoleDimensions, ConsoleOptions, RenderableType
from rich.control import Control
from rich.protocol import is_renderable
from rich.segment import Segment, Segments
from rich.terminal_theme import TerminalTheme

from textual import (
    Logger,
    LogGroup,
    LogVerbosity,
    actions,
    constants,
    events,
    log,
    messages,
    on,
)
from textual._animator import DEFAULT_EASING, Animatable, Animator, EasingFunction
from textual._ansi_sequences import SYNC_END, SYNC_START
from textual._ansi_theme import ALABASTER, MONOKAI
from textual._callback import invoke
from textual._compat import cached_property
from textual._compositor import CompositorUpdate
from textual._context import active_app, active_message_pump
from textual._context import message_hook as message_hook_context_var
from textual._dispatch_key import dispatch_key
from textual._event_broker import NoHandler, extract_handler_actions
from textual._files import generate_datetime_filename
from textual._path import (
    CSSPathType,
    _css_path_type_as_list,
    _make_path_object_relative,
)
from textual._types import AnimationLevel
from textual._wait import wait_for_idle
from textual.actions import ActionParseResult, SkipAction
from textual.await_complete import AwaitComplete
from textual.await_remove import AwaitRemove
from textual.binding import Binding, BindingsMap, BindingType, Keymap
from textual.command import CommandListItem, CommandPalette, Provider, SimpleProvider
from textual.compose import compose
from textual.content import Content
from textual.css.errors import StylesheetError
from textual.css.query import NoMatches
from textual.css.stylesheet import RulesMap, Stylesheet
from textual.dom import DOMNode, NoScreen
from textual.driver import Driver
from textual.errors import NoWidget
from textual.features import FeatureFlag, parse_features
from textual.file_monitor import FileMonitor
from textual.filter import ANSIToTruecolor, DimFilter, Monochrome, NoColor
from textual.geometry import Offset, Region, Size
from textual.keys import (
    REPLACED_KEYS,
    _character_to_key,
    _get_unicode_name_from_key,
    _normalize_key_list,
    format_key,
)
from textual.messages import CallbackType, Prune
from textual.notifications import Notification, Notifications, Notify, SeverityLevel
from textual.reactive import Reactive
from textual.renderables.blank import Blank
from textual.screen import (
    ActiveBinding,
    Screen,
    ScreenResultCallbackType,
    ScreenResultType,
    SystemModalScreen,
)
from textual.signal import Signal
from textual.theme import BUILTIN_THEMES, Theme, ThemeProvider
from textual.timer import Timer
from textual.visual import SupportsVisual, Visual
from textual.widget import AwaitMount, Widget
from textual.widgets._toast import ToastRack
from textual.worker import NoActiveWorker, get_current_worker
from textual.worker_manager import WorkerManager

if TYPE_CHECKING:
    from textual_dev.client import DevtoolsClient
    from typing_extensions import Coroutine, Literal, Self, TypeAlias

    from textual._types import MessageTarget

    # Unused & ignored imports are needed for the docs to link to these objects:
    from textual.css.query import WrongType  # type: ignore  # noqa: F401
    from textual.filter import LineFilter
    from textual.message import Message
    from textual.pilot import Pilot
    from textual.system_commands import SystemCommandsProvider
    from textual.widget import MountError  # type: ignore  # noqa: F401

WINDOWS = sys.platform == "win32"

# asyncio will warn against resources not being cleared
if constants.DEBUG:
    warnings.simplefilter("always", ResourceWarning)

# `asyncio.get_event_loop()` is deprecated since Python 3.10:
_ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED = sys.version_info >= (3, 10, 0)

ComposeResult = Iterable[Widget]
RenderResult: TypeAlias = "RenderableType | Visual | SupportsVisual"
"""Result of Widget.render()"""

AutopilotCallbackType: TypeAlias = (
    "Callable[[Pilot[object]], Coroutine[Any, Any, None]]"
)
"""Signature for valid callbacks that can be used to control apps."""

CommandCallback: TypeAlias = "Callable[[], Awaitable[Any]] | Callable[[], Any]"
"""Signature for callbacks used in [`get_system_commands`][textual.app.App.get_system_commands]"""

ScreenType = TypeVar("ScreenType", bound=Screen)
"""Type var for a Screen, used in [`get_screen`][textual.app.App.get_screen]."""


class SystemCommand(NamedTuple):
    """Defines a system command used in the command palette (yielded from [`get_system_commands`][textual.app.App.get_system_commands])."""

    title: str
    """The title of the command (used in search)."""
    help: str
    """Additional help text, shown under the title."""
    callback: CommandCallback
    """A callback to invoke when the command is selected."""
    discover: bool = True
    """Should the command show when the search is empty?"""


def get_system_commands_provider() -> type[SystemCommandsProvider]:
    """Callable to lazy load the system commands.

    Returns:
        System commands class.
    """
    from textual.system_commands import SystemCommandsProvider

    return SystemCommandsProvider


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


class SuspendNotSupported(Exception):
    """Raised if suspending the application is not supported.

    This exception is raised if [`App.suspend`][textual.app.App.suspend] is called while
    the application is running in an environment where this isn't supported.
    """


class InvalidThemeError(Exception):
    """Raised when an invalid theme is set."""


ReturnType = TypeVar("ReturnType")
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
        color: $foreground;

        &:ansi {
            background: ansi_default;
            color: ansi_default;

            .-ansi-scrollbar {
                scrollbar-background: ansi_default;
                scrollbar-background-hover: ansi_default;
                scrollbar-background-active: ansi_default;
                scrollbar-color: ansi_blue;
                scrollbar-color-active: ansi_bright_blue;
                scrollbar-color-hover: ansi_bright_blue;    
                scrollbar-corner-color: ansi_default;           
            }

            .bindings-table--key {
                color: ansi_magenta;
            }
            .bindings-table--description {
                color: ansi_default;
            }

            .bindings-table--header {
                color: ansi_default;
            }

            .bindings-table--divider {
                color: transparent;
                text-style: dim;
            }
        }

        /* When a widget is maximized */
        Screen.-maximized-view {                    
            layout: vertical !important;
            hatch: right $panel;
            overflow-y: auto !important;
            align: center middle;
            .-maximized {
                dock: initial !important;                
            }
        }
        /* Fade the header title when app is blurred */
        &:blur HeaderTitle {           
            text-opacity: 50%;           
        }
    }
    *:disabled:can-focus {
        opacity: 0.7;
    }
    """

    MODES: ClassVar[dict[str, str | Callable[[], Screen]]] = {}
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
    DEFAULT_MODE: ClassVar[str] = "_default"
    """Name of the default mode."""

    SCREENS: ClassVar[dict[str, Callable[[], Screen[Any]]]] = {}
    """Screens associated with the app for the lifetime of the app."""

    AUTO_FOCUS: ClassVar[str | None] = "*"
    """A selector to determine what to focus automatically when a screen is activated.

    The widget focused is the first that matches the given [CSS selector](/guide/queries/#query-selectors).
    Setting to `None` or `""` disables auto focus.
    """

    ALLOW_SELECT: ClassVar[bool] = True
    """A switch to toggle arbitrary text selection for the app.
    
    Note that this doesn't apply to Input and TextArea which have builtin support for selection.
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

    NOTIFICATION_TIMEOUT: ClassVar[float] = 5
    """Default number of seconds to show notifications before removing them."""

    COMMANDS: ClassVar[set[type[Provider] | Callable[[], type[Provider]]]] = {
        get_system_commands_provider
    }
    """Command providers used by the [command palette](/guide/command_palette).

    Should be a set of [command.Provider][textual.command.Provider] classes.
    """

    COMMAND_PALETTE_BINDING: ClassVar[str] = "ctrl+p"
    """The key that launches the command palette (if enabled by [`App.ENABLE_COMMAND_PALETTE`][textual.app.App.ENABLE_COMMAND_PALETTE])."""

    COMMAND_PALETTE_DISPLAY: ClassVar[str | None] = None
    """How the command palette key should be displayed in the footer (or `None` for default)."""

    ALLOW_IN_MAXIMIZED_VIEW: ClassVar[str] = "Footer"
    """The default value of [Screen.ALLOW_IN_MAXIMIZED_VIEW][textual.screen.Screen.ALLOW_IN_MAXIMIZED_VIEW]."""

    CLICK_CHAIN_TIME_THRESHOLD: ClassVar[float] = 0.5
    """The maximum number of seconds between clicks to upgrade a single click to a double click, 
    a double click to a triple click, etc."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            tooltip="Quit the app and return to the command prompt.",
            show=False,
            priority=True,
        ),
        Binding("ctrl+c", "help_quit", show=False, system=True),
    ]
    """The default key bindings."""

    CLOSE_TIMEOUT: float | None = 5.0
    """Timeout waiting for widget's to close, or `None` for no timeout."""

    TOOLTIP_DELAY: float = 0.5
    """The time in seconds after which a tooltip gets displayed."""

    BINDING_GROUP_TITLE: str | None = None
    """Set to text to show in the key panel."""

    ESCAPE_TO_MINIMIZE: ClassVar[bool] = True
    """Use escape key to minimize widgets (potentially overriding bindings).
    
    This is the default value, used if the active screen's `ESCAPE_TO_MINIMIZE` is not changed from `None`.
    """

    INLINE_PADDING: ClassVar[int] = 1
    """Number of blank lines above an inline app."""

    SUSPENDED_SCREEN_CLASS: ClassVar[str] = ""
    """Class to apply to suspended screens, or empty string for no class."""

    HORIZONTAL_BREAKPOINTS: ClassVar[list[tuple[int, str]]] | None = []
    """List of horizontal breakpoints for responsive classes.

    This allows for styles to be responsive to the dimensions of the terminal.
    For instance, you might want to show less information, or fewer columns on a narrow displays -- or more information when the terminal is sized wider than usual.
    
    A breakpoint consists of a tuple containing the minimum width where the class should applied, and the name of the class to set.

    Note that only one class name is set, and if you should avoid having more than one breakpoint set for the same size.

    Example:
        ```python
        # Up to 80 cells wide, the app has the class "-normal"
        # 80 - 119 cells wide, the app has the class "-wide"
        # 120 cells or wider, the app has the class "-very-wide"
        HORIZONTAL_BREAKPOINTS = [(0, "-normal"), (80, "-wide"), (120, "-very-wide")]
        ```
    
    """
    VERTICAL_BREAKPOINTS: ClassVar[list[tuple[int, str]]] | None = []
    """List of vertical breakpoints for responsive classes.
    
    Contents are the same as [`HORIZONTAL_BREAKPOINTS`][textual.app.App.HORIZONTAL_BREAKPOINTS], but the integer is compared to the height, rather than the width.
    """

    _PSEUDO_CLASSES: ClassVar[dict[str, Callable[[App[Any]], bool]]] = {
        "focus": lambda app: app.app_focus,
        "blur": lambda app: not app.app_focus,
        "dark": lambda app: app.current_theme.dark,
        "light": lambda app: not app.current_theme.dark,
        "inline": lambda app: app.is_inline,
        "ansi": lambda app: app.ansi_color,
        "nocolor": lambda app: app.no_color,
    }  # type: ignore[assignment]

    title: Reactive[str] = Reactive("", compute=False)
    """The title of the app, displayed in the header."""
    sub_title: Reactive[str] = Reactive("", compute=False)
    """The app's sub-title, combined with [`title`][textual.app.App.title] in the header."""

    app_focus = Reactive(True, compute=False)
    """Indicates if the app has focus.

    When run in the terminal, the app always has focus. When run in the web, the app will
    get focus when the terminal widget has focus.
    """

    theme: Reactive[str] = Reactive(constants.DEFAULT_THEME)
    """The name of the currently active theme."""

    ansi_theme_dark = Reactive(MONOKAI, init=False)
    """Maps ANSI colors to hex colors using a Rich TerminalTheme object while using a dark theme."""

    ansi_theme_light = Reactive(ALABASTER, init=False)
    """Maps ANSI colors to hex colors using a Rich TerminalTheme object while using a light theme."""

    ansi_color = Reactive(False)
    """Allow ANSI colors in UI?"""

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
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
            ansi_color: Allow ANSI colors if `True`, or convert ANSI colors to to RGB if `False`.

        Raises:
            CssPathError: When the supplied CSS path(s) are an unexpected type.
        """
        self._start_time = perf_counter()
        super().__init__(classes=self.DEFAULT_CLASSES)
        self.features: frozenset[FeatureFlag] = parse_features(os.getenv("TEXTUAL", ""))

        self._registered_themes: dict[str, Theme] = {}
        """Themes that have been registered with the App using `App.register_theme`.
        
        This excludes the built-in themes."""

        for theme in BUILTIN_THEMES.values():
            self.register_theme(theme)

        ansi_theme = (
            self.ansi_theme_dark if self.current_theme.dark else self.ansi_theme_light
        )
        self.set_reactive(App.ansi_color, ansi_color)
        self._filters: list[LineFilter] = [
            ANSIToTruecolor(ansi_theme, enabled=not ansi_color)
        ]
        environ = dict(os.environ)
        self.no_color = environ.pop("NO_COLOR", None) is not None
        if self.no_color:
            self._filters.append(NoColor() if self.ansi_color else Monochrome())

        for filter_name in constants.FILTERS.split(","):
            filter = filter_name.lower().strip()
            if filter == "dim":
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
            soft_wrap=False,
        )
        self._workers = WorkerManager(self)
        self.error_console = Console(markup=False, highlight=False, stderr=True)
        self.driver_class = driver_class or self.get_driver_class()
        self._screen_stacks: dict[str, list[Screen[Any]]] = {self.DEFAULT_MODE: []}
        """A stack of screens per mode."""
        self._current_mode: str = self.DEFAULT_MODE
        """The current mode the app is in."""
        self._sync_available = False

        self.mouse_over: Widget | None = None
        """The widget directly under the mouse."""
        self.hover_over: Widget | None = None
        """The first widget with a hover style under the mouse."""
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._action_targets = {"app", "screen", "focused"}
        self._animator = Animator(self)
        self._animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)

        self._mouse_down_widget: Widget | None = None
        """The widget that was most recently mouse downed (used to create click events)."""

        self._click_chain_last_offset: Offset | None = None
        """The last offset at which a Click occurred, in screen-space."""

        self._click_chain_last_time: float | None = None
        """The last time at which a Click occurred."""

        self._chained_clicks: int = 1
        """Counter which tracks the number of clicks received in a row."""

        self._previous_cursor_position = Offset(0, 0)
        """The previous cursor position"""

        self.cursor_position = Offset(0, 0)
        """The position of the terminal cursor in screen-space.

        This can be set by widgets and is useful for controlling the
        positioning of OS IME and emoji popup menus."""

        self._exception: Exception | None = None
        """The unhandled exception which is leading to the app shutting down,
        or None if the app is still running with no unhandled exceptions."""

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

        self._logger = Logger(self._log, app=self)

        self._css_has_errors = False

        self.theme_variables: dict[str, str] = {}
        """Variables generated from the current theme."""

        # Note that the theme must be set *before* self.get_css_variables() is called
        # to ensure that the variables are retrieved from the currently active theme.
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

        self._keymap: Keymap = {}

        # Sensitivity on X is double the sensitivity on Y to account for
        # cells being twice as tall as wide
        self.scroll_sensitivity_x: float = 4.0
        """Number of columns to scroll in the X direction with wheel or trackpad."""
        self.scroll_sensitivity_y: float = 2.0
        """Number of lines to scroll in the Y direction with wheel or trackpad."""

        self._installed_screens: dict[str, Screen | Callable[[], Screen]] = {}
        self._installed_screens.update(**self.SCREENS)
        self._modes: dict[str, str | Callable[[], Screen]] = self.MODES.copy()
        """Contains the working-copy of the `MODES` for each instance."""

        self._compose_stacks: list[list[Widget]] = []
        self._composed: list[list[Widget]] = []
        self._recompose_required = False

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
            if watch_css or self.debug
            else None
        )
        self._screenshot: str | None = None
        self._dom_ready = False
        self._batch_count = 0
        self._notifications = Notifications()

        self._capture_print: WeakKeyDictionary[MessageTarget, tuple[bool, bool]] = (
            WeakKeyDictionary()
        )
        """Registry of the MessageTargets which are capturing output at any given time."""
        self._capture_stdout = _PrintCapture(self, stderr=False)
        """File-like object capturing data written to stdout."""
        self._capture_stderr = _PrintCapture(self, stderr=True)
        """File-like object capturing data written to stderr."""
        self._original_stdout = sys.__stdout__
        """The original stdout stream (before redirection etc)."""
        self._original_stderr = sys.__stderr__
        """The original stderr stream (before redirection etc)."""

        self.theme_changed_signal: Signal[Theme] = Signal(self, "theme-changed")
        """Signal that is published when the App's theme is changed.
        
        Subscribers will receive the new theme object as an argument to the callback.
        """

        self.app_suspend_signal: Signal[App] = Signal(self, "app-suspend")
        """The signal that is published when the app is suspended.

        When [`App.suspend`][textual.app.App.suspend] is called this signal
        will be [published][textual.signal.Signal.publish];
        [subscribe][textual.signal.Signal.subscribe] to this signal to
        perform work before the suspension takes place.
        """
        self.app_resume_signal: Signal[App] = Signal(self, "app-resume")
        """The signal that is published when the app is resumed after a suspend.

        When the app is resumed after a
        [`App.suspend`][textual.app.App.suspend] call this signal will be
        [published][textual.signal.Signal.publish];
        [subscribe][textual.signal.Signal.subscribe] to this signal to
        perform work after the app has resumed.
        """

        self.set_class(self.current_theme.dark, "-dark-mode", update=False)
        self.set_class(not self.current_theme.dark, "-light-mode", update=False)

        self.animation_level: AnimationLevel = constants.TEXTUAL_ANIMATIONS
        """Determines what type of animations the app will display.

        See [`textual.constants.TEXTUAL_ANIMATIONS`][textual.constants.TEXTUAL_ANIMATIONS].
        """

        self._last_focused_on_app_blur: Widget | None = None
        """The widget that had focus when the last `AppBlur` happened.

        This will be used to restore correct focus when an `AppFocus`
        happens.
        """

        self._previous_inline_height: int | None = None
        """Size of previous inline update."""

        self._resize_event: events.Resize | None = None
        """A pending resize event, sent on idle."""

        self._size: Size | None = None

        self._css_update_count: int = 0
        """Incremented when CSS is invalidated."""

        self._clipboard: str = ""
        """Contents of local clipboard."""

        self.supports_smooth_scrolling: bool = False
        """Does the terminal support smooth scrolling?"""

        self._compose_screen: Screen | None = None
        """The screen composed by App.compose."""

        if self.ENABLE_COMMAND_PALETTE:
            for _key, binding in self._bindings:
                if binding.action in {"command_palette", "app.command_palette"}:
                    break
            else:
                self._bindings._add_binding(
                    Binding(
                        self.COMMAND_PALETTE_BINDING,
                        "command_palette",
                        "palette",
                        show=False,
                        key_display=self.COMMAND_PALETTE_DISPLAY,
                        priority=True,
                        tooltip="Open the command palette",
                    )
                )

    def get_line_filters(self) -> Sequence[LineFilter]:
        """Get currently enabled line filters.

        Returns:
            A list of [LineFilter][textual.filters.LineFilter] instances.
        """
        return [filter for filter in self._filters if filter.enabled]

    @property
    def _is_devtools_connected(self) -> bool:
        """Is the app connected to the devtools?"""
        return self.devtools is not None and self.devtools.is_connected

    @cached_property
    def _exception_event(self) -> asyncio.Event:
        """An event that will be set when the first exception is encountered."""
        return asyncio.Event()

    def __init_subclass__(cls, *args, **kwargs) -> None:
        for variable_name, screen_collection in (
            ("SCREENS", cls.SCREENS),
            ("MODES", cls.MODES),
        ):
            for screen_name, screen_object in screen_collection.items():
                if not (isinstance(screen_object, str) or callable(screen_object)):
                    if isinstance(screen_object, Screen):
                        raise ValueError(
                            f"{variable_name} should contain a Screen type or callable, not an instance"
                            f" (got instance of {type(screen_object).__name__} for {screen_name!r})"
                        )
                    raise TypeError(
                        f"expected a callable or string, got {screen_object!r}"
                    )

        return super().__init_subclass__(*args, **kwargs)

    def _thread_init(self):
        """Initialize threading primitives for the current thread.

        https://github.com/Textualize/textual/issues/5845

        """
        self._message_queue
        self._mounted_event
        self._exception_event
        self._thread_id = threading.get_ident()

    def _get_dom_base(self) -> DOMNode:
        """When querying from the app, we want to query the default screen."""
        return self.default_screen

    def validate_title(self, title: Any) -> str:
        """Make sure the title is set to a string."""
        return str(title)

    def validate_sub_title(self, sub_title: Any) -> str:
        """Make sure the subtitle is set to a string."""
        return str(sub_title)

    @property
    def default_screen(self) -> Screen:
        """The default screen instance."""
        return self.screen if self._compose_screen is None else self._compose_screen

    @property
    def workers(self) -> WorkerManager:
        """The [worker](/guide/workers/) manager.

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
        If the app hasn't exited yet, this will be `None`.

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
            return (
                next(
                    screen
                    for screen in reversed(self._screen_stack)
                    if not isinstance(screen, SystemModalScreen)
                ),
            )
        except StopIteration:
            return ()

    @property
    def clipboard(self) -> str:
        """The value of the local clipboard.

        Note, that this only contains text copied in the app, and not
        text copied from elsewhere in the OS.
        """
        return self._clipboard

    def format_title(self, title: str, sub_title: str) -> Content:
        """Format the title for display.

        Args:
            title: The title.
            sub_title: The sub title.

        Returns:
            Content instance with title and subtitle.
        """
        title_content = Content(title)
        sub_title_content = Content(sub_title)
        if sub_title_content:
            return Content.assemble(
                title_content,
                (" — ", "dim"),
                sub_title_content.stylize("dim"),
            )
        else:
            return title_content

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

    def delay_update(self, delay: float = 0.05) -> None:
        """Delay updates for a short period of time.

        May be used to mask a brief transition.
        Consider this method only if you aren't able to use `App.batch_update`.

        Args:
            delay: Delay before updating.
        """
        self._begin_batch()

        def end_batch() -> None:
            """Re-enable updates, and refresh screen."""
            self._end_batch()
            if not self._batch_count:
                self.screen.refresh()

        self.set_timer(delay, end_batch, name="delay_update")

    @contextmanager
    def _context(self) -> Generator[None, None, None]:
        """Context manager to set ContextVars."""
        app_reset_token = active_app.set(self)
        message_pump_reset_token = active_message_pump.set(self)
        try:
            yield
        finally:
            active_message_pump.reset(message_pump_reset_token)
            active_app.reset(app_reset_token)

    def _watch_ansi_color(self, ansi_color: bool) -> None:
        """Enable or disable the truecolor filter when the reactive changes"""
        for filter in self._filters:
            if isinstance(filter, ANSIToTruecolor):
                filter.enabled = not ansi_color

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
        level: AnimationLevel = "full",
    ) -> None:
        """Animate an attribute.

        See the guide for how to use the [animation](/guide/animation) system.

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation.
            duration: The duration (in seconds) of the animation.
            speed: The speed of the animation.
            delay: A delay (in seconds) before the animation starts.
            easing: An easing method.
            on_complete: A callable to invoke when the animation is finished.
            level: Minimum level required for the animation to take place (inclusive).
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
            level=level,
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
    def is_dom_root(self) -> bool:
        """Is this a root node (i.e. the App)?"""
        return True

    @property
    def is_attached(self) -> bool:
        """Is this node linked to the app through the DOM?"""
        return True

    @property
    def debug(self) -> bool:
        """Is debug mode enabled?"""
        return "debug" in self.features or constants.DEBUG

    @property
    def is_headless(self) -> bool:
        """Is the app running in 'headless' mode?

        Headless mode is used when running tests with [run_test][textual.app.App.run_test].
        """
        return False if self._driver is None else self._driver.is_headless

    @property
    def is_inline(self) -> bool:
        """Is the app running in 'inline' mode?"""
        return False if self._driver is None else self._driver.is_inline

    @property
    def is_web(self) -> bool:
        """Is the app running in 'web' mode via a browser?"""
        return False if self._driver is None else self._driver.is_web

    @property
    def screen_stack(self) -> list[Screen[Any]]:
        """A snapshot of the current screen stack.

        Returns:
            A snapshot of the current state of the screen stack.
        """
        return self._screen_stacks[self._current_mode].copy()

    @property
    def _screen_stack(self) -> list[Screen[Any]]:
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

    @property
    def console_options(self) -> ConsoleOptions:
        """Get options for the Rich console.

        Returns:
            Console options (same object returned from `console.options`).
        """
        size = ConsoleDimensions(*self.size)
        console = self.console
        return ConsoleOptions(
            max_height=size.height,
            size=size,
            legacy_windows=console.legacy_windows,
            min_width=1,
            max_width=size.width,
            encoding=console.encoding,
            is_terminal=console.is_terminal,
        )

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
        focused = self.screen.focused
        if focused is not None and focused.loading:
            return None
        return focused

    @property
    def active_bindings(self) -> dict[str, ActiveBinding]:
        """Get currently active bindings.

        If no widget is focused, then app-level bindings are returned.
        If a widget is focused, then any bindings present in the active screen and app are merged and returned.

        This property may be used to inspect current bindings.

        Returns:
            A dict that maps keys on to binding information.
        """
        return self.screen.active_bindings

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """A generator of system commands used in the command palette.

        Args:
            screen: The screen where the command palette was invoked from.

        Implement this method in your App subclass if you want to add custom commands.
        Here is an example:

        ```python
        def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
            yield from super().get_system_commands(screen)
            yield SystemCommand("Bell", "Ring the bell", self.bell)
        ```

        !!! note
            Requires that [`SystemCommandsProvider`][textual.system_commands.SystemCommandsProvider] is in `App.COMMANDS` class variable.

        Yields:
            [SystemCommand][textual.app.SystemCommand] instances.
        """
        if not self.ansi_color:
            yield SystemCommand(
                "Change theme",
                "Change the current theme",
                self.action_change_theme,
            )
        yield SystemCommand(
            "Quit the application",
            "Quit the application as soon as possible",
            self.action_quit,
        )

        if screen.query("HelpPanel"):
            yield SystemCommand(
                "Hide keys and help panel",
                "Hide the keys and widget help panel",
                self.action_hide_help_panel,
            )
        else:
            yield SystemCommand(
                "Show keys and help panel",
                "Show help for the focused widget and a summary of available keys",
                self.action_show_help_panel,
            )

        if screen.maximized is not None:
            yield SystemCommand(
                "Minimize",
                "Minimize the widget and restore to normal size",
                screen.action_minimize,
            )
        elif screen.focused is not None and screen.focused.allow_maximize:
            yield SystemCommand(
                "Maximize", "Maximize the focused widget", screen.action_maximize
            )

        yield SystemCommand(
            "Save screenshot",
            "Save an SVG 'screenshot' of the current screen",
            lambda: self.set_timer(0.1, self.deliver_screenshot),
        )

    def get_default_screen(self) -> Screen:
        """Get the default screen.

        This is called when the App is first composed. The returned screen instance
        will be the first screen on the stack.

        Implement this method if you would like to use a custom Screen as the default screen.

        Returns:
            A screen instance.
        """
        return Screen(id="_default")

    def compose(self) -> ComposeResult:
        """Yield child widgets for a container.

        This method should be implemented in a subclass.
        """
        yield from ()

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """Get the default values for the `variables` used in a theme.

        If the currently specified theme doesn't define a value for a variable,
        the value specified here will be used as a fallback.

        If a variable is referenced in CSS but does not appear either here
        or in the theme, the CSS will fail to parse on startup.

        This method allows applications to define their own variables, beyond
        those offered by Textual, which can then be overridden by a Theme.

        Returns:
            A mapping of variable name (e.g. "my-button-background-color") to value.
            Values can be any valid CSS value, e.g. "red 50%", "auto 90%",
            "#ff0000", "rgb(255, 0, 0)", etc.
        """
        return {}

    def get_css_variables(self) -> dict[str, str]:
        """Get a mapping of variables used to pre-populate CSS.

        May be implemented in a subclass to add new CSS variables.

        Returns:
            A mapping of variable name to value.
        """
        theme = self.current_theme
        # Build the Textual color system from the theme.
        # This will contain $secondary, $primary, $background, etc.
        variables = theme.to_color_system().generate()
        # Apply the additional variables from the theme
        variables = {**variables, **(theme.variables)}
        theme_variables = self.get_theme_variable_defaults()

        combined_variables = {**theme_variables, **variables}
        self.theme_variables = combined_variables
        return combined_variables

    def get_theme(self, theme_name: str) -> Theme | None:
        """Get a theme by name.

        Args:
            theme_name: The name of the theme to get. May also be a comma
                separated list of names, to pick the first available theme.

        Returns:
            A Theme instance and None if the theme doesn't exist.
        """
        theme_names = [token.strip() for token in theme_name.split(",")]
        for theme_name in theme_names:
            if theme_name in self.available_themes:
                return self.available_themes[theme_name]
        return None

    def register_theme(self, theme: Theme) -> None:
        """Register a theme with the app.

        If the theme already exists, it will be overridden.

        After registering a theme, you can activate it by setting the
        `App.theme` attribute. To retrieve a registered theme, use the
        `App.get_theme` method.

        Args:
            theme: The theme to register.
        """
        self._registered_themes[theme.name] = theme

    def unregister_theme(self, theme_name: str) -> None:
        """Unregister a theme with the app.

        Args:
            theme_name: The name of the theme to unregister.
        """
        if theme_name in self._registered_themes:
            del self._registered_themes[theme_name]

    @property
    def available_themes(self) -> dict[str, Theme]:
        """All available themes (all built-in themes plus any that have been registered).

        A dictionary mapping theme names to Theme instances.
        """
        return {**self._registered_themes}

    @property
    def current_theme(self) -> Theme:
        theme = self.get_theme(self.theme)
        if theme is None:
            theme = self.get_theme("textual-dark")
        assert theme is not None  # validated by _validate_theme
        return theme

    def _validate_theme(self, theme_name: str) -> str:
        if theme_name not in self.available_themes:
            message = (
                f"Theme {theme_name!r} has not been registered. "
                "Call 'App.register_theme' before setting the 'App.theme' attribute."
            )
            raise InvalidThemeError(message)
        return theme_name

    def _watch_theme(self, theme_name: str) -> None:
        """Apply a theme to the application.

        This method is called when the theme reactive attribute is set.
        """
        theme = self.current_theme
        dark = theme.dark
        self.ansi_color = theme_name == "textual-ansi"
        self.set_class(dark, "-dark-mode", update=False)
        self.set_class(not dark, "-light-mode", update=False)
        self._refresh_truecolor_filter(self.ansi_theme)
        self._invalidate_css()
        self.call_next(partial(self.refresh_css, animate=False))
        self.call_next(self.theme_changed_signal.publish, theme)

    def _invalidate_css(self) -> None:
        """Invalidate CSS, so it will be refreshed."""
        self._css_update_count += 1

    def watch_ansi_theme_dark(self, theme: TerminalTheme) -> None:
        if self.current_theme.dark:
            self._refresh_truecolor_filter(theme)
            self._invalidate_css()
            self.call_next(self.refresh_css)

    def watch_ansi_theme_light(self, theme: TerminalTheme) -> None:
        if not self.current_theme.dark:
            self._refresh_truecolor_filter(theme)
            self._invalidate_css()
            self.call_next(self.refresh_css)

    @property
    def ansi_theme(self) -> TerminalTheme:
        """The ANSI TerminalTheme currently being used.

        Defines how colors defined as ANSI (e.g. `magenta`) inside Rich renderables
        are mapped to hex codes.
        """
        return (
            self.ansi_theme_dark if self.current_theme.dark else self.ansi_theme_light
        )

    def _refresh_truecolor_filter(self, theme: TerminalTheme) -> None:
        """Update the ANSI to Truecolor filter, if available, with a new theme mapping.

        Args:
            theme: The new terminal theme to use for mapping ANSI to truecolor.
        """
        filters = self._filters
        for index, filter in enumerate(filters):
            if isinstance(filter, ANSIToTruecolor):
                filters[index] = ANSIToTruecolor(theme, enabled=not self.ansi_color)
                return

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
            from textual.drivers.windows_driver import WindowsDriver

            driver_class = WindowsDriver
        else:
            from textual.drivers.linux_driver import LinuxDriver

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
        """The animator object."""
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
        if self._size is not None:
            return self._size
        if self._driver is not None and self._driver._size is not None:
            width, height = self._driver._size
        else:
            width, height = self.console.size
        return Size(width, height)

    @property
    def viewport_size(self) -> Size:
        """Get the viewport size (size of the screen)."""
        try:
            return self.screen.size
        except (ScreenStackError, NoScreen):
            return self.size

    def _get_inline_height(self) -> int:
        """Get the inline height (height when in inline mode).

        Returns:
            Height in lines.
        """
        size = self.size
        return max(screen._get_inline_height(size) for screen in self._screen_stack)

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

        Positional args will be logged. Keyword args will be prefixed with the key.

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

    def get_loading_widget(self) -> Widget:
        """Get a widget to be used as a loading indicator.

        Extend this method if you want to display the loading state a little differently.

        Returns:
            A widget to display a loading state.
        """
        from textual.widgets import LoadingIndicator

        return LoadingIndicator()

    def copy_to_clipboard(self, text: str) -> None:
        """Copy text to the clipboard.

        !!! note

            This does not work on macOS Terminal, but will work on most other terminals.

        Args:
            text: Text you wish to copy to the clipboard.
        """
        self._clipboard = text
        if self._driver is None:
            return
        import base64

        base64_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        self._driver.write(f"\x1b]52;c;{base64_text}\a")

    def call_from_thread(
        self,
        callback: Callable[..., CallThreadReturnType | Awaitable[CallThreadReturnType]],
        *args: Any,
        **kwargs: Any,
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
            with self._context():
                return await invoke(callback_with_args)

        # Post the message to the main loop
        future: Future[CallThreadReturnType] = asyncio.run_coroutine_threadsafe(
            run_callback(), loop=self._loop
        )
        result = future.result()
        return result

    def action_change_theme(self) -> None:
        """An [action](/guide/actions) to change the current theme."""
        self.search_themes()

    def action_screenshot(
        self, filename: str | None = None, path: str | None = None
    ) -> None:
        """This [action](/guide/actions) will save an SVG file containing the current contents of the screen.

        Args:
            filename: Filename of screenshot, or None to auto-generate.
            path: Path to directory. Defaults to the user's Downloads directory.
        """
        self.deliver_screenshot(filename, path)

    def export_screenshot(
        self,
        *,
        title: str | None = None,
        simplify: bool = False,
    ) -> str:
        """Export an SVG screenshot of the current screen.

        See also [save_screenshot][textual.app.App.save_screenshot] which writes the screenshot to a file.

        Args:
            title: The title of the exported screenshot or None
                to use app title.
            simplify: Simplify the segments by combining contiguous segments with the same style.
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
            full=True, screen_stack=self.app._background_screens, simplify=simplify
        )
        console.print(screen_render)
        return console.export_svg(title=title or self.title)

    def save_screenshot(
        self,
        filename: str | None = None,
        path: str | None = None,
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
        path = path or "./"
        if not filename:
            svg_filename = generate_datetime_filename(self.title, ".svg", time_format)
        else:
            svg_filename = filename
        svg_path = os.path.expanduser(os.path.join(path, svg_filename))
        screenshot_svg = self.export_screenshot()
        with open(svg_path, "w", encoding="utf-8") as svg_file:
            svg_file.write(screenshot_svg)
        return svg_path

    def deliver_screenshot(
        self,
        filename: str | None = None,
        path: str | None = None,
        time_format: str | None = None,
    ) -> str | None:
        """Deliver a screenshot of the app.

        This with save the screenshot when running locally, or serve it when the app
        is running in a web browser.

        Args:
            filename: Filename of SVG screenshot, or None to auto-generate
                a filename with the date and time.
            path: Path to directory for output when saving locally (not used when app is running in the browser).
                Defaults to current working directory.
            time_format: Date and time format to use if filename is None.
                Defaults to a format like ISO 8601 with some reserved characters replaced with underscores.

        Returns:
            The delivery key that uniquely identifies the file delivery.
        """
        if not filename:
            svg_filename = generate_datetime_filename(self.title, ".svg", time_format)
        else:
            svg_filename = filename
        screenshot_svg = self.export_screenshot()
        return self.deliver_text(
            io.StringIO(screenshot_svg),
            save_directory=path,
            save_filename=svg_filename,
            open_method="browser",
            mime_type="image/svg+xml",
            name="screenshot",
        )

    def search_commands(
        self,
        commands: Sequence[CommandListItem],
        placeholder: str = "Search for commands…",
    ) -> AwaitMount:
        """Show a list of commands in the app.

        Args:
            commands: A list of SimpleCommand instances.
            placeholder: Placeholder text for the search field.

        Returns:
            AwaitMount: An awaitable that resolves when the commands are shown.
        """
        return self.push_screen(
            CommandPalette(
                providers=[SimpleProvider(self.screen, commands)],
                placeholder=placeholder,
            )
        )

    def search_themes(self) -> None:
        """Show a fuzzy search command palette containing all registered themes.

        Selecting a theme in the list will change the app's theme.
        """
        self.push_screen(
            CommandPalette(
                providers=[ThemeProvider],
                placeholder="Search for themes…",
            ),
        )

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

        !!! warning
            This method may be private or removed in a future version of Textual.
            See [dynamic actions](/guide/actions#dynamic-actions) for a more flexible alternative to updating bindings.

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

    def get_key_display(self, binding: Binding) -> str:
        """Format a bound key for display in footer / key panel etc.

        !!! note
            You can implement this in a subclass if you want to change how keys are displayed in your app.

        Args:
            binding: A Binding.

        Returns:
            A string used to represent the key.
        """
        # Dev has overridden the key display, so use that
        if binding.key_display:
            return binding.key_display

        # Extract modifiers
        modifiers, key = binding.parse_key()

        # Format the key (replace unicode names with character)
        key = format_key(key)

        # Convert ctrl modifier to caret
        if "ctrl" in modifiers:
            modifiers.pop(modifiers.index("ctrl"))
            key = f"^{key}"
        # Join everything with +
        key_tokens = modifiers + [key]
        return "+".join(key_tokens)

    async def _press_keys(self, keys: Iterable[str]) -> None:
        """A task to send key events."""
        import unicodedata

        app = self
        driver = app._driver
        assert driver is not None
        for key in keys:
            if key.startswith("wait:"):
                _, wait_ms = key.split(":")
                await asyncio.sleep(float(wait_ms) / 1000)
                await app._animator.wait_until_complete()
            else:
                if len(key) == 1 and not key.isalnum():
                    key = _character_to_key(key)
                original_key = REPLACED_KEYS.get(key, key)
                char: str | None
                try:
                    char = unicodedata.lookup(_get_unicode_name_from_key(original_key))
                except KeyError:
                    char = key if len(key) == 1 else None
                key_event = events.Key(key, char)
                key_event.set_sender(app)
                driver.send_message(key_event)
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
        from textual.pilot import Pilot

        app = self
        app._disable_tooltips = not tooltips
        app._disable_notifications = not notifications
        app_ready_event = asyncio.Event()

        def on_app_ready() -> None:
            """Called when app is ready to process events."""
            app_ready_event.set()

        async def run_app(app: App[ReturnType]) -> None:
            """Run the apps message loop.

            Args:
                app: App to run.
            """

            with app._context():
                try:
                    if message_hook is not None:
                        message_hook_context_var.set(message_hook)
                    app._loop = asyncio.get_running_loop()
                    app._thread_id = threading.get_ident()
                    await app._process_messages(
                        ready_callback=on_app_ready,
                        headless=headless,
                        terminal_size=size,
                    )
                finally:
                    app_ready_event.set()

        # Launch the app in the "background"

        self._task = app_task = create_task(run_app(app), name=f"run_test {app}")

        # Wait until the app has performed all startup routines.
        await app_ready_event.wait()
        with app._context():
            # Context manager returns pilot object to manipulate the app
            try:
                pilot = Pilot(app)
                await pilot._wait_for_screen()
                yield pilot
            finally:
                await asyncio.sleep(0)
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
        inline: bool = False,
        inline_no_clear: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> ReturnType | None:
        """Run the app asynchronously.

        Args:
            headless: Run in headless mode (no output).
            inline: Run the app inline (under the prompt).
            inline_no_clear: Don't clear the app output when exiting an inline app.
            mouse: Enable mouse support.
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect.
            auto_pilot: An autopilot coroutine.

        Returns:
            App return value.
        """
        from textual.pilot import Pilot

        app = self
        auto_pilot_task: Task | None = None

        if auto_pilot is None and constants.PRESS:
            keys = constants.PRESS.split(",")

            async def press_keys(pilot: Pilot[ReturnType]) -> None:
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
                    with self._context():
                        try:
                            await auto_pilot(pilot)
                        except Exception:
                            app.exit()
                            raise

                pilot = Pilot(app)
                auto_pilot_task = create_task(
                    run_auto_pilot(auto_pilot, pilot), name=repr(pilot)
                )

        self._thread_init()

        loop = app._loop = asyncio.get_running_loop()
        if hasattr(asyncio, "eager_task_factory"):
            loop.set_task_factory(asyncio.eager_task_factory)
        with app._context():
            try:
                await app._process_messages(
                    ready_callback=None if auto_pilot is None else app_ready,
                    headless=headless,
                    inline=inline,
                    inline_no_clear=inline_no_clear,
                    mouse=mouse,
                    terminal_size=size,
                )
            finally:
                try:
                    if auto_pilot_task is not None:
                        await auto_pilot_task
                finally:
                    try:
                        await asyncio.shield(app._shutdown())
                    except asyncio.CancelledError:
                        pass
                app._loop = None
                app._thread_id = 0

        return app.return_value

    def run(
        self,
        *,
        headless: bool = False,
        inline: bool = False,
        inline_no_clear: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
        loop: AbstractEventLoop | None = None,
    ) -> ReturnType | None:
        """Run the app.

        Args:
            headless: Run in headless mode (no output).
            inline: Run the app inline (under the prompt).
            inline_no_clear: Don't clear the app output when exiting an inline app.
            mouse: Enable mouse support.
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect.
            auto_pilot: An auto pilot coroutine.
            loop: Asyncio loop instance, or `None` to use default.
        Returns:
            App return value.
        """

        async def run_app() -> ReturnType | None:
            """Run the app."""
            return await self.run_async(
                headless=headless,
                inline=inline,
                inline_no_clear=inline_no_clear,
                mouse=mouse,
                size=size,
                auto_pilot=auto_pilot,
            )

        if loop is None:
            if _ASYNCIO_GET_EVENT_LOOP_IS_DEPRECATED:
                # N.B. This does work with Python<3.10, but global Locks, Events, etc
                # eagerly bind the event loop, and result in Future bound to wrong
                # loop errors.
                return asyncio.run(run_app())
            try:
                global_loop = asyncio.get_event_loop()
            except RuntimeError:
                # the global event loop may have been destroyed by someone running
                # asyncio.run(), or asyncio.set_event_loop(None), in which case
                # we need to use asyncio.run() also. (We run this outside the
                # context of an exception handler)
                pass
            else:
                return global_loop.run_until_complete(run_app())
            return asyncio.run(run_app())
        return loop.run_until_complete(run_app())

    async def _on_css_change(self) -> None:
        """Callback for the file monitor, called when CSS files change."""
        css_paths = (
            self.css_monitor._paths if self.css_monitor is not None else self.css_path
        )
        if css_paths:
            try:
                time = perf_counter()
                stylesheet = self.stylesheet.copy()
                try:
                    stylesheet.read_all(css_paths)
                except StylesheetError as error:
                    # If one of the CSS paths is no longer available (or perhaps temporarily unavailable),
                    #  we'll end up with partial CSS, which is probably confusing more than anything. We opt to do
                    #  nothing here, knowing that we'll retry again very soon, on the next file monitor invocation.
                    #  Related issue: https://github.com/Textualize/textual/issues/3996
                    self.log.warning(str(error))
                    return
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
                for screen in self.screen_stack:
                    self.stylesheet.update(screen)

    def render(self) -> RenderResult:
        """Render method, inherited from widget, to render the screen's background.

        May be overridden to customize background visuals.

        """
        return Blank(self.styles.background)

    ExpectType = TypeVar("ExpectType", bound=Widget)

    if TYPE_CHECKING:

        @overload
        def get_child_by_id(self, id: str) -> Widget: ...

        @overload
        def get_child_by_id(
            self, id: str, expect_type: type[ExpectType]
        ) -> ExpectType: ...

    def get_child_by_id(
        self, id: str, expect_type: type[ExpectType] | None = None
    ) -> ExpectType | Widget:
        """Get the first child (immediate descendant) of this DOMNode with the given ID.

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

    if TYPE_CHECKING:

        @overload
        def get_widget_by_id(self, id: str) -> Widget: ...

        @overload
        def get_widget_by_id(
            self, id: str, expect_type: type[ExpectType]
        ) -> ExpectType: ...

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
        """Do internal initialization of a new screen stack mode.

        Args:
            mode: Name of the mode.

        Returns:
            An optionally awaitable object which can be awaited until the screen
            associated with the mode has been mounted.
        """

        stack = self._screen_stacks.get(mode, [])
        if stack:
            # Mode already exists
            # Return an dummy await
            return AwaitMount(stack[0], [])

        if mode in self._modes:
            # Mode is defined in MODES
            _screen = self._modes[mode]
            if isinstance(_screen, Screen):
                raise TypeError(
                    "MODES cannot contain instances, use a type instead "
                    f"(got instance of {type(_screen).__name__} for {mode!r})"
                )
            new_screen: Screen | str = _screen() if callable(_screen) else _screen
            screen, await_mount = self._get_screen(new_screen)
            stack.append(screen)
            self._load_screen_css(screen)
            if screen._css_update_count != self._css_update_count:
                self.refresh_css()

            screen.post_message(events.ScreenResume())
        else:
            # Mode is not defined
            screen = self.get_default_screen()
            stack.append(screen)
            self._register(self, screen)
            screen.post_message(events.ScreenResume())
            await_mount = AwaitMount(stack[0], [])

        screen._screen_resized(self.size)

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

        if mode == self._current_mode:
            return AwaitMount(self.screen, [])

        if mode not in self._modes:
            raise UnknownModeError(f"No known mode {mode!r}")

        self.screen.post_message(events.ScreenSuspend())
        self.screen.refresh()

        if mode not in self._screen_stacks:
            await_mount = self._init_mode(mode)
        else:
            await_mount = AwaitMount(self.screen, [])

        self._current_mode = mode
        if self.screen._css_update_count != self._css_update_count:
            self.refresh_css()
        self.screen._screen_resized(self.size)
        self.screen.post_message(events.ScreenResume())

        self.log.system(f"{self._current_mode!r} is the current mode")
        self.log.system(f"{self.screen} is active")

        return await_mount

    def add_mode(self, mode: str, base_screen: str | Callable[[], Screen]) -> None:
        """Adds a mode and its corresponding base screen to the app.

        Args:
            mode: The new mode.
            base_screen: The base screen associated with the given mode.

        Raises:
            InvalidModeError: If the name of the mode is not valid/duplicated.
        """
        if mode == "_default":
            raise InvalidModeError("Cannot use '_default' as a custom mode.")
        elif mode in self._modes:
            raise InvalidModeError(f"Duplicated mode name {mode!r}.")

        if isinstance(base_screen, Screen):
            raise TypeError(
                "add_mode() must be called with a Screen type, not an instance"
                f" (got instance of {type(base_screen).__name__})"
            )
        self._modes[mode] = base_screen

    def remove_mode(self, mode: str) -> AwaitComplete:
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
        elif mode not in self._modes:
            raise UnknownModeError(f"Unknown mode {mode!r}")
        else:
            del self._modes[mode]

        if mode not in self._screen_stacks:
            return AwaitComplete.nothing()

        stack = self._screen_stacks[mode]
        del self._screen_stacks[mode]

        async def remove_screens() -> None:
            """Remove screens."""
            for screen in reversed(stack):
                await self._replace_screen(screen)

        return AwaitComplete(remove_screens()).call_next(self)

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

    @overload
    def get_screen(self, screen: ScreenType) -> ScreenType: ...

    @overload
    def get_screen(self, screen: str) -> Screen: ...

    @overload
    def get_screen(
        self, screen: str, screen_class: Type[ScreenType] | None = None
    ) -> ScreenType: ...

    @overload
    def get_screen(
        self, screen: ScreenType, screen_class: Type[ScreenType] | None = None
    ) -> ScreenType: ...

    def get_screen(
        self, screen: Screen | str, screen_class: Type[Screen] | None = None
    ) -> Screen:
        """Get an installed screen.

        Example:
            ```python
            my_screen = self.get_screen("settings", MyScreen)
            ```

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).
            screen_class: Class of expected screen, or `None` for any screen class.

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
        if screen_class is not None and not isinstance(next_screen, screen_class):
            raise TypeError(
                f"Expected a screen of type {screen_class}, got {type(next_screen)}"
            )
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
            if not self.stylesheet.has_source(str(path), ""):
                self.stylesheet.read(path)
                update = True
        if screen.CSS:
            try:
                screen_path = inspect.getfile(screen.__class__)
            except (TypeError, OSError):
                screen_path = ""
            screen_class_var = f"{screen.__class__.__name__}.CSS"
            read_from = (screen_path, screen_class_var)
            if not self.stylesheet.has_source(screen_path, screen_class_var):
                self.stylesheet.add_source(
                    screen.CSS,
                    read_from=read_from,
                    is_default_css=False,
                    scope=screen._css_type_name if screen.SCOPED_CSS else "",
                )
                update = True
        if update:
            self.stylesheet.reparse()
            self.stylesheet.update(self)

    async def _replace_screen(self, screen: Screen) -> Screen:
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
            self.capture_mouse(None)
            await screen.remove()
            self.log.system(f"{screen} REMOVED")
        return screen

    if TYPE_CHECKING:

        @overload
        def push_screen(
            self,
            screen: Screen[ScreenResultType] | str,
            callback: ScreenResultCallbackType[ScreenResultType] | None = None,
            wait_for_dismiss: Literal[False] = False,
        ) -> AwaitMount: ...

        @overload
        def push_screen(
            self,
            screen: Screen[ScreenResultType] | str,
            callback: ScreenResultCallbackType[ScreenResultType] | None = None,
            wait_for_dismiss: Literal[True] = True,
        ) -> asyncio.Future[ScreenResultType]: ...

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

        self.app.capture_mouse(None)
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
        next_screen._update_auto_focus()
        self._screen_stack.append(next_screen)
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

    if TYPE_CHECKING:

        @overload
        async def push_screen_wait(
            self, screen: Screen[ScreenResultType]
        ) -> ScreenResultType: ...

        @overload
        async def push_screen_wait(self, screen: str) -> Any: ...

    async def push_screen_wait(
        self, screen: Screen[ScreenResultType] | str
    ) -> ScreenResultType | Any:
        """Push a screen and wait for the result (received from [`Screen.dismiss`][textual.screen.Screen.dismiss]).

        Note that this method may only be called when running in a worker.

        Args:
            screen: A screen or the name of an installed screen.

        Returns:
            The screen's result.
        """
        await self._flush_next_callbacks()
        # The shield prevents the cancellation of the current task from canceling the push_screen awaitable
        return await asyncio.shield(self.push_screen(screen, wait_for_dismiss=True))

    def switch_screen(self, screen: Screen | str) -> AwaitComplete:
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
            return AwaitComplete.nothing()

        self.app.capture_mouse(None)
        top_screen = self._screen_stack.pop()

        top_screen._pop_result_callback()
        self._load_screen_css(next_screen)
        self._screen_stack.append(next_screen)
        self.screen.post_message(events.ScreenResume())
        self.screen._push_result_callback(self.screen, None)
        self.log.system(f"{self.screen} is current (SWITCHED)")

        async def do_switch() -> None:
            """Task to perform switch."""

            await await_mount()
            await self._replace_screen(top_screen)

        return AwaitComplete(do_switch()).call_next(self)

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
                f"Can't install screen; {screen!r} has already been installed"
            )
        self._installed_screens[name] = screen
        self.log.system(f"{screen} INSTALLED name={name!r}")

    def uninstall_screen(self, screen: Screen | str) -> str | None:
        """Uninstall a screen.

        If the screen was not previously installed, then this method is a null-op.
        Uninstalling a screen allows Textual to delete it when it is popped or switched.
        Note that uninstalling a screen is only required if you have previously installed it
        with [install_screen][textual.app.App.install_screen].
        Textual will also uninstall screens automatically on exit.

        Args:
            screen: The screen to uninstall or the name of an installed screen.

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

    def pop_screen(self) -> AwaitComplete:
        """Pop the current [screen](/guide/screens) from the stack, and switch to the previous screen.

        Returns:
            The screen that was replaced.
        """

        screen_stack = self._screen_stack
        if len(screen_stack) <= 1:
            raise ScreenStackError(
                "Can't pop screen; there must be at least one screen on the stack"
            )

        previous_screen = screen_stack.pop()
        previous_screen._pop_result_callback()
        self.screen.post_message(events.ScreenResume())
        self.log.system(f"{self.screen} is active")

        async def do_pop() -> None:
            """Task to pop the screen."""
            await self._replace_screen(previous_screen)

        return AwaitComplete(do_pop()).call_next(self)

    def _pop_to_screen(self, screen: Screen) -> None:
        """Pop screens until the given screen is active.

        Args:
            screen: desired active screen

        Raises:
            ScreenError: If the screen doesn't exist in the stack.
        """
        screens_to_pop: list[Screen] = []
        for pop_screen in reversed(self.screen_stack):
            if pop_screen is not screen:
                screens_to_pop.append(pop_screen)
            else:
                break
        else:
            raise ScreenError(f"Screen {screen!r} not in screen stack")

        async def pop_screens() -> None:
            """Pop any screens in `screens_to_pop`."""
            with self.batch_update():
                for screen in screens_to_pop:
                    await screen.dismiss()

        if screens_to_pop:
            self.call_later(pop_screens)

    def set_focus(self, widget: Widget | None, scroll_visible: bool = True) -> None:
        """Focus (or unfocus) a widget. A focused widget will receive key events first.

        Args:
            widget: Widget to focus.
            scroll_visible: Scroll widget into view.
        """
        self.screen.set_focus(widget, scroll_visible)

    def _set_mouse_over(
        self, widget: Widget | None, hover_widget: Widget | None
    ) -> None:
        """Called when the mouse is over another widget.

        Args:
            widget: Widget under mouse, or None for no widgets.
        """
        if widget is None:
            if self.mouse_over is not None:
                try:
                    self.mouse_over.post_message(events.Leave(self.mouse_over))
                finally:
                    self.mouse_over = None
        else:
            if self.mouse_over is not widget:
                try:
                    if self.mouse_over is not None:
                        self.mouse_over.post_message(events.Leave(self.mouse_over))
                    if widget is not None:
                        widget.post_message(events.Enter(widget))
                finally:
                    self.mouse_over = widget
        if self.hover_over is not None:
            self.hover_over.mouse_hover = False
        if hover_widget is not None:
            hover_widget.mouse_hover = True

        self.hover_over = hover_widget

    def _update_mouse_over(self, screen: Screen) -> None:
        """Updates the mouse over after the next refresh.

        This method is called whenever a widget is added or removed, which may change
        the widget under the mouse.

        """

        if self.mouse_over is None or not screen.is_active:
            return

        async def check_mouse() -> None:
            """Check if the mouse over widget has changed."""
            try:
                hover_widgets = screen.get_hover_widgets_at(*self.mouse_position)
            except NoWidget:
                pass
            else:
                mouse_over, hover_over = hover_widgets.widgets
                if (
                    mouse_over is not self.mouse_over
                    or hover_over is not self.hover_over
                ):
                    self._set_mouse_over(mouse_over, hover_over)

        self.call_after_refresh(check_mouse)

    def capture_mouse(self, widget: Widget | None) -> None:
        """Send all mouse events to the given widget or disable mouse capture.

        Normally mouse events are sent to the widget directly under the pointer.
        Capturing the mouse allows a widget to receive mouse events even when the pointer is over another widget.

        Args:
            widget: Widget to capture mouse events, or `None` to end mouse capture.
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
        if self._exception is None:
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
        from rich.traceback import Traceback

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

    def _build_driver(
        self, headless: bool, inline: bool, mouse: bool, size: tuple[int, int] | None
    ) -> Driver:
        """Construct a driver instance.

        Args:
            headless: Request headless driver.
            inline: Request inline driver.
            mouse: Request mouse support.
            size: Initial size.

        Returns:
            Driver instance.
        """
        driver: Driver
        driver_class: type[Driver]
        if headless:
            from textual.drivers.headless_driver import HeadlessDriver

            driver_class = HeadlessDriver
        elif inline and not WINDOWS:
            from textual.drivers.linux_inline_driver import LinuxInlineDriver

            driver_class = LinuxInlineDriver
        else:
            driver_class = self.driver_class

        driver = self._driver = driver_class(
            self,
            debug=constants.DEBUG,
            mouse=mouse,
            size=size,
        )
        return driver

    async def _init_devtools(self):
        """Initialize developer tools."""
        if self.devtools is not None:
            from textual_dev.client import DevtoolsConnectionError

            try:
                await self.devtools.connect()
                self.log.system(f"Connected to devtools ( {self.devtools.url} )")
            except DevtoolsConnectionError:
                self.log.system(f"Couldn't connect to devtools ( {self.devtools.url} )")

    async def _process_messages(
        self,
        ready_callback: CallbackType | None = None,
        headless: bool = False,
        inline: bool = False,
        inline_no_clear: bool = False,
        mouse: bool = True,
        terminal_size: tuple[int, int] | None = None,
        message_hook: Callable[[Message], None] | None = None,
    ) -> None:
        self._thread_init()

        async def app_prelude() -> bool:
            """Work required before running the app.

            Returns:
                `True` if the app should continue, or `False` if there was a problem starting.
            """
            await self._init_devtools()
            self.log.system("---")
            self.log.system(loop=asyncio.get_running_loop())
            self.log.system(features=self.features)
            if constants.LOG_FILE is not None:
                _log_path = os.path.abspath(constants.LOG_FILE)
                self.log.system(f"Writing logs to {_log_path!r}")

            try:
                if self.css_path:
                    self.stylesheet.read_all(self.css_path)
                for read_from, css, tie_breaker, scope in self._get_default_css():
                    self.stylesheet.add_source(
                        css,
                        read_from=read_from,
                        is_default_css=True,
                        tie_breaker=tie_breaker,
                        scope=scope,
                    )
                if self.CSS:
                    try:
                        app_path = inspect.getfile(self.__class__)
                    except (TypeError, OSError):
                        app_path = ""
                    read_from = (app_path, f"{self.__class__.__name__}.CSS")
                    self.stylesheet.add_source(
                        self.CSS, read_from=read_from, is_default_css=False
                    )
            except Exception as error:
                self._handle_exception(error)
                self._print_error_renderables()
                return False

            if self.css_monitor:
                self.set_interval(0.25, self.css_monitor, name="css monitor")
                self.log.system("STARTED", self.css_monitor)
            return True

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
                        await self._dispatch_message(
                            events.Resize.from_dimensions(self.size, None)
                        )
                        default_screen = self.screen
                        self.stylesheet.apply(self)
                        await self._dispatch_message(events.Mount())
                        self.check_idle()
                    finally:
                        self._mounted_event.set()
                        self._is_mounted = True

                    Reactive._initialize_object(self)

                    if self.screen is not default_screen:
                        self.stylesheet.apply(default_screen)

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
                    await Timer._stop_all(self._timers)

        with self._context():
            if not await app_prelude():
                return
            self._running = True
            try:
                load_event = events.Load()
                await self._dispatch_message(load_event)

                driver = self._driver = self._build_driver(
                    headless=headless,
                    inline=inline,
                    mouse=mouse,
                    size=terminal_size,
                )
                self.log(driver=driver)

                if not self._exit:
                    driver.start_application_mode()
                    try:
                        with redirect_stdout(self._capture_stdout):
                            with redirect_stderr(self._capture_stderr):
                                await run_process_messages()

                    finally:
                        Reactive._clear_watchers(self)
                        if self._driver.is_inline:
                            cursor_x, cursor_y = self._previous_cursor_position
                            self._driver.write(
                                Control.move(-cursor_x, -cursor_y).segment.text
                            )
                            self._driver.flush()
                            if inline_no_clear and not self.app._exit_renderables:
                                console = Console()
                                try:
                                    console.print(self.screen._compositor)
                                except ScreenStackError:
                                    console.print()
                            else:
                                self._driver.write(
                                    Control.move(0, -self.INLINE_PADDING).segment.text
                                )

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
        self.log.system(f"ready in {ready_time:0.0f} milliseconds")

        async def take_screenshot() -> None:
            """Take a screenshot and exit."""
            self.save_screenshot(
                path=constants.SCREENSHOT_LOCATION,
                filename=constants.SCREENSHOT_FILENAME,
            )
            self.exit()

        if constants.SCREENSHOT_DELAY >= 0:
            self.set_timer(
                constants.SCREENSHOT_DELAY, take_screenshot, name="screenshot timer"
            )

    async def _on_compose(self) -> None:
        _rich_traceback_omit = True
        self._compose_screen = self.screen
        try:
            widgets = [*self.screen._nodes, *compose(self)]
        except TypeError as error:
            raise TypeError(
                f"{self!r} compose() method returned an invalid result; {error}"
            ) from error

        await self.mount_all(widgets)

    async def _check_recompose(self) -> None:
        """Check if a recompose is required."""
        if self._recompose_required:
            self._recompose_required = False
            await self.recompose()

    async def recompose(self) -> None:
        """Recompose the widget.

        Recomposing will remove children and call `self.compose` again to remount.
        """
        if self._exit:
            return
        try:
            async with self.screen.batch():
                await self.screen.query("*").exclude(".-textual-system").remove()
                await self.screen.mount_all(compose(self))
        except ScreenStackError:
            pass

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
                # list, if after isn't -1.
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

    def _register(
        self,
        parent: DOMNode,
        *widgets: Widget,
        before: int | None = None,
        after: int | None = None,
        cache: dict[tuple, RulesMap] | None = None,
    ) -> list[Widget]:
        """Register widget(s) so they may receive events.

        Args:
            parent: Parent node.
            *widgets: The widget(s) to register.
            before: A location to mount before.
            after: A location to mount after.
            cache: Optional rules map cache.

        Returns:
            List of modified widgets.
        """

        if not widgets:
            return []

        if cache is None:
            cache = {}
        widget_list: Iterable[Widget]
        if before is not None or after is not None:
            # There's a before or after, which means there's going to be an
            # insertion, so make it easier to get the new things in the
            # correct order.
            widget_list = reversed(widgets)
        else:
            widget_list = widgets

        apply_stylesheet = self.stylesheet.apply
        new_widgets: list[Widget] = []
        add_new_widget = new_widgets.append
        for widget in widget_list:
            widget._closing = False
            widget._closed = False
            widget._pruning = False
            if not isinstance(widget, Widget):
                raise AppError(f"Can't register {widget!r}; expected a Widget instance")
            if widget not in self._registry:
                add_new_widget(widget)
                self._register_child(parent, widget, before, after)
                if widget._nodes:
                    self._register(widget, *widget._nodes, cache=cache)
        for widget in new_widgets:
            apply_stylesheet(widget, cache=cache)
            widget._start_messages()

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
        """Start a widget (run its task) so that it can receive messages.

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
                    await self._prune(stack_screen)
            stack.clear()
        self._installed_screens.clear()
        self._modes.clear()

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

        self._nodes._clear()

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
        self._message_queue.put_nowait(None)

    def refresh(
        self,
        *,
        repaint: bool = True,
        layout: bool = False,
        recompose: bool = False,
    ) -> Self:
        """Refresh the entire screen.

        Args:
            repaint: Repaint the widget (will call render() again).
            layout: Also layout widgets in the view.
            recompose: Re-compose the widget (will remove and re-mount children).

        Returns:
            The `App` instance.
        """
        if recompose:
            self._recompose_required = recompose
            self.call_next(self._check_recompose)
            return self

        if self._screen_stack:
            self.screen.refresh(repaint=repaint, layout=layout)
        self.check_idle()
        return self

    def refresh_css(self, animate: bool = True) -> None:
        """Refresh CSS.

        Args:
            animate: Also execute CSS animations.
        """
        stylesheet = self.app.stylesheet
        stylesheet.set_variables(self.get_css_variables())
        stylesheet.reparse()
        stylesheet.update(self.app, animate=animate)
        try:
            if self.screen.is_mounted:
                self.screen._refresh_layout(self.size)
                self.screen._css_update_count = self._css_update_count
        except ScreenError:
            pass
        # The other screens in the stack will need to know about some style
        # changes, as a final pass let's check in on every screen that isn't
        # the current one and update them too.
        for screen in self.screen_stack:
            if screen != self.screen:
                stylesheet.update(screen, animate=animate)
                screen._css_update_count = self._css_update_count

    def _display(self, screen: Screen, renderable: RenderableType | None) -> None:
        """Display a renderable within a sync.

        Args:
            screen: Screen instance
            renderable: A Rich renderable.
        """

        try:
            if renderable is None:
                return
            if self._batch_count:
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
                            cursor_position = self.screen.outer_size.clamp_offset(
                                self.cursor_position
                            )
                            if self._driver.is_inline:
                                terminal_sequence = Control.move(
                                    *(-self._previous_cursor_position)
                                ).segment.text
                                terminal_sequence += renderable.render_segments(console)
                                terminal_sequence += Control.move(
                                    *cursor_position
                                ).segment.text
                            else:
                                terminal_sequence = renderable.render_segments(console)
                                terminal_sequence += Control.move_to(
                                    *cursor_position
                                ).segment.text
                            self._previous_cursor_position = cursor_position
                        else:
                            segments = console.render(renderable)
                            terminal_sequence = console._render_buffer(segments)
                    except Exception as error:
                        self._handle_exception(error)
                    else:
                        if WINDOWS:
                            # Combat a problem with Python on Windows.
                            #
                            # https://github.com/Textualize/textual/issues/2548
                            # https://github.com/python/cpython/issues/82052
                            CHUNK_SIZE = 8192
                            write = self._driver.write
                            for chunk in (
                                terminal_sequence[offset : offset + CHUNK_SIZE]
                                for offset in range(
                                    0, len(terminal_sequence), CHUNK_SIZE
                                )
                            ):
                                write(chunk)
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
    def _binding_chain(self) -> list[tuple[DOMNode, BindingsMap]]:
        """Get a chain of nodes and bindings to consider.

        If no widget is focused, returns the bindings from both the screen and the app level bindings.
        Otherwise, combines all the bindings from the currently focused node up the DOM to the root App.
        """
        focused = self.focused
        namespace_bindings: list[tuple[DOMNode, BindingsMap]]

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

    def simulate_key(self, key: str) -> None:
        """Simulate a key press.

        This will perform the same action as if the user had pressed the key.

        Args:
            key: Key to simulate. May also be the name of a key, e.g. "space".
        """
        self.post_message(events.Key(key, None))

    async def _check_bindings(self, key: str, priority: bool = False) -> bool:
        """Handle a key press.

        This method is used internally by the bindings system.

        Args:
            key: A key.
            priority: If `True` check from `App` down, otherwise from focused up.

        Returns:
            True if the key was handled by a binding, otherwise False
        """
        for namespace, bindings in (
            reversed(self.screen._binding_chain)
            if priority
            else self.screen._modal_binding_chain
        ):
            key_bindings = bindings.key_to_bindings.get(key, ())
            for binding in key_bindings:
                if binding.priority == priority:
                    if await self.run_action(binding.action, namespace):
                        return True
        return False

    def action_help_quit(self) -> None:
        """Bound to ctrl+C to alert the user that it no longer quits."""
        # Doing this because users will reflexively hit ctrl+C to exit
        # Ctrl+C is now bound to copy if an input / textarea is focused.
        # This makes is possible, even likely, that a user may do it accidentally -- which would be maddening.
        # Rather than do nothing, we can make an educated guess the user was trying
        # to quit, and inform them how you really quit.
        for key, active_binding in self.active_bindings.items():
            if active_binding.binding.action in ("quit", "app.quit"):
                self.notify(
                    f"Press [b]{key}[/b] to quit the app", title="Do you want to quit?"
                )
                return

    @classmethod
    def _normalize_keymap(cls, keymap: Keymap) -> Keymap:
        """Normalizes the keys in a keymap, so they use long form, i.e. "question_mark" rather than "?"."""
        return {
            binding_id: _normalize_key_list(keys) for binding_id, keys in keymap.items()
        }

    def set_keymap(self, keymap: Keymap) -> None:
        """Set the keymap, a mapping of binding IDs to key strings.

        Bindings in the keymap are used to override default key bindings,
        i.e. those defined in `BINDINGS` class variables.

        Bindings with IDs that are present in the keymap will have
        their key string replaced with the value from the keymap.

        Args:
            keymap: A mapping of binding IDs to key strings.
        """

        self._keymap = self._normalize_keymap(keymap)
        self.refresh_bindings()

    def update_keymap(self, keymap: Keymap) -> None:
        """Update the App's keymap, merging with `keymap`.

        If a Binding ID exists in both the App's keymap and the `keymap`
        argument, the `keymap` argument takes precedence.

        Args:
            keymap: A mapping of binding IDs to key strings.
        """

        self._keymap = {**self._keymap, **self._normalize_keymap(keymap)}
        self.refresh_bindings()

    def handle_bindings_clash(
        self, clashed_bindings: set[Binding], node: DOMNode
    ) -> None:
        """Handle a clash between bindings.

        Bindings clashes are likely due to users setting conflicting
        keys via their keymap.

        This method is intended to be overridden by subclasses.

        Textual will call this each time a clash is encountered -
        which may be on each keypress if a clashing widget is focused
        or is in the bindings chain.

        Args:
            clashed_bindings: The bindings that are clashing.
            node: The node that has the clashing bindings.
        """
        pass

    async def on_event(self, event: events.Event) -> None:
        # Handle input events that haven't been forwarded
        # If the event has been forwarded it may have bubbled up back to the App
        if isinstance(event, events.Compose):
            await self._init_mode(self._current_mode)
            await super().on_event(event)
        elif isinstance(event, events.InputEvent) and not event.is_forwarded:
            if not self.app_focus and isinstance(event, (events.Key, events.MouseDown)):
                self.app_focus = True
            if isinstance(event, events.MouseEvent):
                # Record current mouse position on App
                self.mouse_position = Offset(event.x, event.y)
                if isinstance(event, events.MouseDown):
                    try:
                        self._mouse_down_widget, _ = self.get_widget_at(
                            event.x, event.y
                        )
                    except NoWidget:
                        # Shouldn't occur, since at the very least this will find the Screen
                        self._mouse_down_widget = None

                self.screen._forward_event(event)

                # If a MouseUp occurs at the same widget as a MouseDown, then we should
                # consider it a click, and produce a Click event.
                if (
                    isinstance(event, events.MouseUp)
                    and self._mouse_down_widget is not None
                ):
                    try:
                        screen_offset = event.screen_offset
                        mouse_down_widget = self._mouse_down_widget
                        mouse_up_widget, _ = self.get_widget_at(*screen_offset)
                        if mouse_up_widget is mouse_down_widget:
                            same_offset = (
                                self._click_chain_last_offset is not None
                                and self._click_chain_last_offset == screen_offset
                            )
                            within_time_threshold = (
                                self._click_chain_last_time is not None
                                and event.time - self._click_chain_last_time
                                <= self.CLICK_CHAIN_TIME_THRESHOLD
                            )

                            if same_offset and within_time_threshold:
                                self._chained_clicks += 1
                            else:
                                self._chained_clicks = 1

                            click_event = events.Click.from_event(
                                mouse_down_widget, event, chain=self._chained_clicks
                            )

                            self._click_chain_last_time = event.time
                            self._click_chain_last_offset = screen_offset

                            self.screen._forward_event(click_event)
                    except NoWidget:
                        pass

            elif isinstance(event, events.Key):
                # Special case for maximized widgets
                # If something is maximized, then escape should minimize
                if (
                    self.screen.maximized is not None
                    and event.key == "escape"
                    and self.escape_to_minimize
                ):
                    self.screen.minimize()
                    return
                if self.focused:
                    try:
                        self.screen._clear_tooltip()
                    except NoScreen:
                        pass
                if not await self._check_bindings(event.key, priority=True):
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

    @property
    def escape_to_minimize(self) -> bool:
        """Use the escape key to minimize?

        When a widget is [maximized][textual.screen.Screen.maximize], this boolean determines if the `escape` key will
        minimize the widget (potentially overriding any bindings).

        The default logic is to use the screen's `ESCAPE_TO_MINIMIZE` classvar if it is set to `True` or `False`.
        If the classvar on the screen is *not* set (and left as `None`), then the app's `ESCAPE_TO_MINIMIZE` is used.

        """
        return bool(
            self.ESCAPE_TO_MINIMIZE
            if self.screen.ESCAPE_TO_MINIMIZE is None
            else self.screen.ESCAPE_TO_MINIMIZE
        )

    def _parse_action(
        self,
        action: str | ActionParseResult,
        default_namespace: DOMNode,
        namespaces: Mapping[str, DOMNode] | None = None,
    ) -> tuple[DOMNode, str, tuple[object, ...]]:
        """Parse an action.

        Args:
            action: An action string.
            default_namespace: Namespace to user when none is supplied in the action.
            namespaces: Mapping of namespaces.

        Raises:
            ActionError: If there are any errors parsing the action string.

        Returns:
            A tuple of (node or None, action name, tuple of parameters).
        """
        if isinstance(action, tuple):
            destination, action_name, params = action
        else:
            destination, action_name, params = actions.parse(action)

        action_target: DOMNode | None = (
            None if namespaces is None else namespaces.get(destination)
        )
        if destination and action_target is None:
            if destination not in self._action_targets:
                raise ActionError(f"Action namespace {destination} is not known")
            action_target = getattr(self, destination, None)
            if action_target is None:
                raise ActionError(f"Action target {destination!r} not available")
        return (
            (default_namespace if action_target is None else action_target),
            action_name,
            params,
        )

    def _check_action_state(
        self, action: str, default_namespace: DOMNode
    ) -> bool | None:
        """Check if an action is enabled.

        Args:
            action: An action string.
            default_namespace: The default namespace if one is not specified in the action.

        Returns:
            State of an action.
        """
        action_target, action_name, parameters = self._parse_action(
            action, default_namespace
        )
        return action_target.check_action(action_name, parameters)

    async def run_action(
        self,
        action: str | ActionParseResult,
        default_namespace: DOMNode | None = None,
        namespaces: Mapping[str, DOMNode] | None = None,
    ) -> bool:
        """Perform an [action](/guide/actions).

        Actions are typically associated with key bindings, where you wouldn't need to call this method manually.

        Args:
            action: Action encoded in a string.
            default_namespace: Namespace to use if not provided in the action,
                or None to use app.
            namespaces: Mapping of namespaces.

        Returns:
            True if the event has been handled.
        """
        action_target, action_name, params = self._parse_action(
            action, self if default_namespace is None else default_namespace, namespaces
        )
        if action_target.check_action(action_name, params):
            return await self._dispatch_action(action_target, action_name, params)
        else:
            return False

    async def _dispatch_action(
        self, namespace: DOMNode, action_name: str, params: Any
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

        log.system(
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
            log.system(
                f"<action> {action_name!r} has no target."
                f" Could not find methods '_action_{action_name}' or 'action_{action_name}'"
            )
        except SkipAction:
            # The action method raised this to explicitly not handle the action
            log.system(f"<action> {action_name!r} skipped.")

        return False

    async def _broker_event(
        self, event_name: str, event: events.Event, default_namespace: DOMNode
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

        if isinstance(action, str):
            await self.run_action(action, default_namespace)
        elif isinstance(action, tuple) and len(action) == 2:
            action_name, action_params = action
            namespace, parsed_action, _ = actions.parse(action_name)
            await self.run_action(
                (namespace, parsed_action, action_params),
                default_namespace,
            )
        else:
            if isinstance(action, tuple) and self.debug:
                # It's a tuple and made it this far, which means it'll be a
                # malformed action. This is a no-op, but let's log that
                # anyway.
                log.warning(
                    f"Can't parse @{event_name} action from style meta; check your console markup syntax"
                )
            return False
        return True

    async def _on_update(self, message: messages.Update) -> None:
        message.stop()

    async def _on_layout(self, message: messages.Layout) -> None:
        message.stop()

    async def _on_key(self, event: events.Key) -> None:
        if not (await self._check_bindings(event.key)):
            await dispatch_key(self, event)

    async def _on_resize(self, event: events.Resize) -> None:
        event.stop()
        self._size = event.size
        self._resize_event = event

    async def _on_app_focus(self, event: events.AppFocus) -> None:
        """App has focus."""
        # Required by textual-web to manage focus in a web page.
        self.app_focus = True
        self.screen.refresh_bindings()

    async def _on_app_blur(self, event: events.AppBlur) -> None:
        """App has lost focus."""
        # Required by textual-web to manage focus in a web page.
        self.app_focus = False
        self.screen.refresh_bindings()

    def _prune(self, *nodes: Widget, parent: DOMNode | None = None) -> AwaitRemove:
        """Prune nodes from DOM.

        Args:
            parent: Parent node.

        Returns:
            Optional awaitable.
        """
        if not nodes:
            return AwaitRemove([])
        pruning_nodes: set[Widget] = {*nodes}
        for node in nodes:
            node.post_message(Prune())
            pruning_nodes.update(node.walk_children(with_self=True))

        try:
            screen = nodes[0].screen
        except (ScreenStackError, NoScreen):
            pass
        else:
            if screen.focused and screen.focused in pruning_nodes:
                screen._reset_focus(screen.focused, list(pruning_nodes))

        for node in pruning_nodes:
            node._pruning = True

        def post_mount() -> None:
            """Called after removing children."""

            if parent is not None:
                try:
                    screen = parent.screen
                except (ScreenStackError, NoScreen):
                    pass
                else:
                    if screen._running:
                        self._update_mouse_over(screen)
                finally:
                    parent.refresh(layout=True)

        await_complete = AwaitRemove(
            [task for node in nodes if (task := node._task) is not None],
            post_mount,
        )
        self.call_next(await_complete)
        return await_complete

    def _watch_app_focus(self, focus: bool) -> None:
        """Respond to changes in app focus."""
        self.screen._update_styles()
        if focus:
            # If we've got a last-focused widget, if it still has a screen,
            # and if the screen is still the current screen and if nothing
            # is focused right now...
            try:
                if (
                    self._last_focused_on_app_blur is not None
                    and self._last_focused_on_app_blur.screen is self.screen
                    and self.screen.focused is None
                ):
                    # ...settle focus back on that widget.
                    # Don't scroll the newly focused widget, as this can be quite jarring
                    self.screen.set_focus(
                        self._last_focused_on_app_blur,
                        scroll_visible=False,
                        from_app_focus=True,
                    )
            except NoScreen:
                pass
            # Now that we have focus back on the app and we don't need the
            # widget reference any more, don't keep it hanging around here.
            self._last_focused_on_app_blur = None
        else:
            # Remember which widget has focus, when the app gets focus back
            # we'll want to try and focus it again.
            self._last_focused_on_app_blur = self.screen.focused
            # Remove focus for now.
            self.screen.set_focus(None)

    async def action_simulate_key(self, key: str) -> None:
        """An [action](/guide/actions) to simulate a key press.

        This will invoke the same actions as if the user had pressed the key.

        Args:
            key: The key to process.
        """
        self.simulate_key(key)

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
        """An [action](/guide/actions) that switches to the given mode."""
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

    def action_toggle_dark(self) -> None:
        """An [action](/guide/actions) to toggle the theme between textual-light
        and textual-dark. This is offered as a convenience to simplify backwards
        compatibility with previous versions of Textual which only had light mode
        and dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_focus_next(self) -> None:
        """An [action](/guide/actions) to focus the next widget."""
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        """An [action](/guide/actions) to focus the previous widget."""
        self.screen.focus_previous()

    def action_hide_help_panel(self) -> None:
        """Hide the keys panel (if present)."""
        self.screen.query("HelpPanel").remove()

    def action_show_help_panel(self) -> None:
        """Show the keys panel."""
        from textual.widgets import HelpPanel

        try:
            self.screen.query_one(HelpPanel)
        except NoMatches:
            self.screen.mount(HelpPanel())

    def action_notify(
        self, message: str, title: str = "", severity: str = "information"
    ) -> None:
        """Show a notification."""
        self.notify(message, title=title, severity=severity)

    def _on_terminal_supports_synchronized_output(
        self, message: messages.TerminalSupportsSynchronizedOutput
    ) -> None:
        log.system("SynchronizedOutput mode is supported")
        if self._driver is not None and not self._driver.is_inline:
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
            self.call_later(toast_rack.show, self._notifications)

    def clear_selection(self) -> None:
        """Clear text selection on the active screen."""
        try:
            self.screen.clear_selection()
        except NoScreen:
            pass

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float | None = None,
        markup: bool = True,
    ) -> None:
        """Create a notification.

        !!! tip

            This method is thread-safe.


        Args:
            message: The message for the notification.
            title: The title for the notification.
            severity: The severity of the notification.
            timeout: The timeout (in seconds) for the notification, or `None` for default.
            markup: Render the message as content markup?

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
        if timeout is None:
            timeout = self.NOTIFICATION_TIMEOUT
        notification = Notification(message, title, severity, timeout, markup=markup)
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
            self.push_screen(CommandPalette(id="--command-palette"))

    def _suspend_signal(self) -> None:
        """Signal that the application is being suspended."""
        self.app_suspend_signal.publish(self)

    @on(Driver.SignalResume)
    def _resume_signal(self) -> None:
        """Signal that the application is being resumed from a suspension."""
        self.app_resume_signal.publish(self)

    @contextmanager
    def suspend(self) -> Iterator[None]:
        """A context manager that temporarily suspends the app.

        While inside the `with` block, the app will stop reading input and
        emitting output. Other applications will have full control of the
        terminal, configured as it was before the app started running. When
        the `with` block ends, the application will start reading input and
        emitting output again.

        Example:
            ```python
            with self.suspend():
                os.system("emacs -nw")
            ```

        Raises:
            SuspendNotSupported: If the environment doesn't support suspending.

        !!! note
            Suspending the application is currently only supported on
            Unix-like operating systems and Microsoft Windows. Suspending is
            not supported in Textual Web.
        """
        if self._driver is None:
            return
        if self._driver.can_suspend:
            # Publish a suspend signal *before* we suspend application mode.
            self._suspend_signal()
            self._driver.suspend_application_mode()
            # We're going to handle the start of the driver again so mark
            # this next part as such; the reason for this is that the code
            # the developer may be running could be in this process, and on
            # Unix-like systems the user may `action_suspend_process` the
            # app, and we don't want to have the driver auto-restart
            # application mode when the application comes back to the
            # foreground, in this context.
            with self._driver.no_automatic_restart(), redirect_stdout(
                sys.__stdout__
            ), redirect_stderr(sys.__stderr__):
                yield
            # We're done with the dev's code so resume application mode.
            self._driver.resume_application_mode()
            # ...and publish a resume signal.
            self._resume_signal()
            self.refresh(layout=True)
        else:
            raise SuspendNotSupported(
                "App.suspend is not supported in this environment."
            )

    def action_suspend_process(self) -> None:
        """Suspend the process into the background.

        Note:
            On Unix and Unix-like systems a `SIGTSTP` is sent to the
            application's process. Currently on Windows and when running
            under Textual Web this is a non-operation.
        """
        # Check if we're in an environment that permits this kind of
        # suspend.
        if not WINDOWS and self._driver is not None and self._driver.can_suspend:
            # First, ensure that the suspend signal gets published while
            # we're still in application mode.
            self._suspend_signal()
            # With that out of the way, send the SIGTSTP signal.
            os.kill(os.getpid(), signal.SIGTSTP)
            # NOTE: There is no call to publish the resume signal here, this
            # will be handled by the driver posting a SignalResume event
            # (see the event handler on App._resume_signal) above.

    def open_url(self, url: str, *, new_tab: bool = True) -> None:
        """Open a URL in the default web browser.

        Args:
            url: The URL to open.
            new_tab: Whether to open the URL in a new tab.
        """
        if self._driver is not None:
            self._driver.open_url(url, new_tab)

    def deliver_text(
        self,
        path_or_file: str | Path | TextIO,
        *,
        save_directory: str | Path | None = None,
        save_filename: str | None = None,
        open_method: Literal["browser", "download"] = "download",
        encoding: str | None = None,
        mime_type: str | None = None,
        name: str | None = None,
    ) -> str | None:
        """Deliver a text file to the end-user of the application.

        If a TextIO object is supplied, it will be closed by this method
        and *must not be used* after this method is called.

        If running in a terminal, this will save the file to the user's
        downloads directory.

        If running via a web browser, this will initiate a download via
        a single-use URL.

        After the file has been delivered, a `DeliveryComplete` message will be posted
        to this `App`, which contains the `delivery_key` returned by this method. By
        handling this message, you can add custom logic to your application that fires
        only after the file has been delivered.

        Args:
            path_or_file: The path or file-like object to save.
            save_directory: The directory to save the file to.
            save_filename: The filename to save the file to.  If `path_or_file`
                is a file-like object, the filename will be generated from
                the `name` attribute if available. If `path_or_file` is a path
                the filename will be generated from the path.
            encoding: The encoding to use when saving the file. If `None`,
                the encoding will be determined by supplied file-like object
                (if possible). If this is not possible, 'utf-8' will be used.
            mime_type: The MIME type of the file or None to guess based on file extension.
                If no MIME type is supplied and we cannot guess the MIME type, from the
                file extension, the MIME type will be set to "text/plain".
            name: A user-defined named which will be returned in [`DeliveryComplete`][textual.events.DeliveryComplete]
                and [`DeliveryComplete`][textual.events.DeliveryComplete].

        Returns:
            The delivery key that uniquely identifies the file delivery.
        """
        # Ensure `path_or_file` is a file-like object - convert if needed.
        if isinstance(path_or_file, (str, Path)):
            binary_path = Path(path_or_file)
            binary = binary_path.open("rb")
            file_name = save_filename or binary_path.name
        else:
            encoding = encoding or getattr(path_or_file, "encoding", None) or "utf-8"
            binary = path_or_file
            file_name = save_filename or getattr(path_or_file, "name", None)

        # If we could infer a filename, and no MIME type was supplied, guess the MIME type.
        if file_name and not mime_type:
            mime_type, _ = mimetypes.guess_type(file_name)

        # Still no MIME type? Default it to "text/plain".
        if mime_type is None:
            mime_type = "text/plain"

        return self._deliver_binary(
            binary,
            save_directory=save_directory,
            save_filename=file_name,
            open_method=open_method,
            encoding=encoding,
            mime_type=mime_type,
            name=name,
        )

    def deliver_binary(
        self,
        path_or_file: str | Path | BinaryIO,
        *,
        save_directory: str | Path | None = None,
        save_filename: str | None = None,
        open_method: Literal["browser", "download"] = "download",
        mime_type: str | None = None,
        name: str | None = None,
    ) -> str | None:
        """Deliver a binary file to the end-user of the application.

        If an IO object is supplied, it will be closed by this method
        and *must not be used* after it is supplied to this method.

        If running in a terminal, this will save the file to the user's
        downloads directory.

        If running via a web browser, this will initiate a download via
        a single-use URL.

        This operation runs in a thread when running on web, so this method
        returning does not indicate that the file has been delivered.

        After the file has been delivered, a `DeliveryComplete` message will be posted
        to this `App`, which contains the `delivery_key` returned by this method. By
        handling this message, you can add custom logic to your application that fires
        only after the file has been delivered.

        Args:
            path_or_file: The path or file-like object to save.
            save_directory: The directory to save the file to. If None,
                the default "downloads" directory will be used. This
                argument is ignored when running via the web.
            save_filename: The filename to save the file to. If None, the following logic
                applies to generate the filename:
                - If `path_or_file` is a file-like object, the filename will be taken from
                  the `name` attribute if available.
                - If `path_or_file` is a path, the filename will be taken from the path.
                - If a filename is not available, a filename will be generated using the
                  App's title and the current date and time.
            open_method: The method to use to open the file. "browser" will open the file in the
                web browser, "download" will initiate a download. Note that this can sometimes
                be impacted by the browser's settings.
            mime_type: The MIME type of the file or None to guess based on file extension.
                If no MIME type is supplied and we cannot guess the MIME type, from the
                file extension, the MIME type will be set to "application/octet-stream".
            name: A user-defined named which will be returned in [`DeliveryComplete`][textual.events.DeliveryComplete]
                and [`DeliveryComplete`][textual.events.DeliveryComplete].

        Returns:
            The delivery key that uniquely identifies the file delivery.
        """
        # Ensure `path_or_file` is a file-like object - convert if needed.
        if isinstance(path_or_file, (str, Path)):
            binary_path = Path(path_or_file)
            binary = binary_path.open("rb")
            file_name = save_filename or binary_path.name
        else:  # IO object
            binary = path_or_file
            file_name = save_filename or getattr(path_or_file, "name", None)

        # If we could infer a filename, and no MIME type was supplied, guess the MIME type.
        if file_name and not mime_type:
            mime_type, _ = mimetypes.guess_type(file_name)

        # Still no MIME type? Default it to "application/octet-stream".
        if mime_type is None:
            mime_type = "application/octet-stream"

        return self._deliver_binary(
            binary,
            save_directory=save_directory,
            save_filename=file_name,
            open_method=open_method,
            mime_type=mime_type,
            encoding=None,
            name=name,
        )

    def _deliver_binary(
        self,
        binary: BinaryIO | TextIO,
        *,
        save_directory: str | Path | None,
        save_filename: str | None,
        open_method: Literal["browser", "download"],
        encoding: str | None = None,
        mime_type: str | None = None,
        name: str | None = None,
    ) -> str | None:
        """Deliver a binary file to the end-user of the application."""
        if self._driver is None:
            return None

        # Generate a filename if the file-like object doesn't have one.
        if save_filename is None:
            save_filename = generate_datetime_filename(self.title, "")

        # Find the appropriate save location if not specified.
        save_directory = (
            user_downloads_path() if save_directory is None else Path(save_directory)
        )

        # Generate a unique key for this delivery
        delivery_key = str(uuid.uuid4().hex)

        # Save the file. The driver will determine the appropriate action
        # to take here. It could mean simply writing to the save_path, or
        # sending the file to the web browser for download.
        self._driver.deliver_binary(
            binary,
            delivery_key=delivery_key,
            save_path=save_directory / save_filename,
            encoding=encoding,
            open_method=open_method,
            mime_type=mime_type,
            name=name,
        )

        return delivery_key

    @on(events.DeliveryComplete)
    def _on_delivery_complete(self, event: events.DeliveryComplete) -> None:
        """Handle a successfully delivered screenshot."""
        if event.name == "screenshot":
            if event.path is None:
                self.notify("Saved screenshot", title="Screenshot")
            else:
                self.notify(
                    f"Saved screenshot to [green]{str(event.path)!r}",
                    title="Screenshot",
                )

    @on(events.DeliveryFailed)
    def _on_delivery_failed(self, event: events.DeliveryComplete) -> None:
        """Handle a failure to deliver the screenshot."""
        if event.name == "screenshot":
            self.notify(
                "Failed to save screenshot", title="Screenshot", severity="error"
            )

    @on(messages.InBandWindowResize)
    def _on_in_band_window_resize(self, message: messages.InBandWindowResize) -> None:
        """In band window resize enables smooth scrolling."""
        self.supports_smooth_scrolling = message.enabled
        self.log.debug(message)

    def _on_idle(self) -> None:
        """Send app resize events on idle, so we don't do more resizing that necessary."""
        event = self._resize_event
        if event is not None:
            self._resize_event = None
            self.screen.post_message(event)
            for screen in self._background_screens:
                screen.post_message(event)
