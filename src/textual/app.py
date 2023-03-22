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
from pathlib import Path, PurePath
from queue import Queue
from time import perf_counter
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
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
from weakref import WeakSet

import rich
import rich.repr
from rich.console import Console, RenderableType
from rich.protocol import is_renderable
from rich.segment import Segment, Segments
from rich.traceback import Traceback

from . import Logger, LogGroup, LogVerbosity, actions, constants, events, log, messages
from ._animator import DEFAULT_EASING, Animatable, Animator, EasingFunction
from ._ansi_sequences import SYNC_END, SYNC_START
from ._asyncio import create_task
from ._callback import invoke
from ._compose import compose
from ._context import active_app, active_message_pump
from ._event_broker import NoHandler, extract_handler_actions
from ._path import _make_path_object_relative
from ._wait import wait_for_idle
from .actions import ActionParseResult, SkipAction
from .await_remove import AwaitRemove
from .binding import Binding, Bindings
from .css.query import NoMatches
from .css.stylesheet import Stylesheet
from .design import ColorSystem
from .dom import DOMNode
from .driver import Driver
from .drivers.headless_driver import HeadlessDriver
from .features import FeatureFlag, parse_features
from .file_monitor import FileMonitor
from .filter import LineFilter, Monochrome
from .geometry import Offset, Region, Size
from .keys import (
    REPLACED_KEYS,
    _character_to_key,
    _get_key_display,
    _get_unicode_name_from_key,
)
from .messages import CallbackType
from .reactive import Reactive
from .renderables.blank import Blank
from .screen import Screen
from .widget import AwaitMount, Widget

if TYPE_CHECKING:
    from typing_extensions import Coroutine, Final, TypeAlias

    from .devtools.client import DevtoolsClient
    from .pilot import Pilot

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

AutopilotCallbackType: TypeAlias = "Callable[[Pilot], Coroutine[Any, Any, None]]"


class AppError(Exception):
    pass


class ActionError(Exception):
    pass


class ScreenError(Exception):
    pass


class ScreenStackError(ScreenError):
    """Raised when attempting to pop the last screen from the stack."""


class CssPathError(Exception):
    """Raised when supplied CSS path(s) are invalid."""


ReturnType = TypeVar("ReturnType")


class _NullFile:
    """A file-like where writes go nowhere."""

    def write(self, text: str) -> None:
        pass

    def flush(self) -> None:
        pass


MAX_QUEUED_WRITES: Final[int] = 30


class _WriterThread(threading.Thread):
    """A thread / file-like to do writes to stdout in the background."""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self._queue: Queue[str | None] = Queue(MAX_QUEUED_WRITES)
        self._file = sys.__stdout__

    def write(self, text: str) -> None:
        """Write text. Text will be enqueued for writing.

        Args:
            text: Text to write to the file.
        """
        self._queue.put(text)

    def isatty(self) -> bool:
        """Pretend to be a terminal.

        Returns:
            True if this is a tty.
        """
        return True

    def fileno(self) -> int:
        """Get file handle number.

        Returns:
            File number of proxied file.
        """
        return self._file.fileno()

    def flush(self) -> None:
        """Flush the file (a no-op, because flush is done in the thread)."""
        return

    def run(self) -> None:
        """Run the thread."""
        write = self._file.write
        flush = self._file.flush
        get = self._queue.get
        qsize = self._queue.qsize
        # Read from the queue, write to the file.
        # Flush when there is a break.
        while True:
            text: str | None = get()
            empty = qsize() == 0
            if text is None:
                break
            write(text)
            if empty:
                flush()

    def stop(self) -> None:
        """Stop the thread, and block until it finished."""
        self._queue.put(None)
        self.join()


CSSPathType = Union[
    str,
    PurePath,
    List[Union[str, PurePath]],
]

CallThreadReturnType = TypeVar("CallThreadReturnType")


@rich.repr.auto
class App(Generic[ReturnType], DOMNode):
    """The base class for Textual Applications.
    Args:
        driver_class: Driver class or ``None`` to auto-detect. Defaults to None.
        css_path: Path to CSS or ``None`` for no CSS file.
            Defaults to None. To load multiple CSS files, pass a list of strings or paths which will be loaded in order.
        watch_css: Watch CSS for changes. Defaults to False.

    Raises:
        CssPathError: When the supplied CSS path(s) are an unexpected type.
    """

    CSS = ""
    """Inline CSS, useful for quick scripts. This is loaded after CSS_PATH,
    and therefore takes priority in the event of a specificity clash."""

    # Default (the lowest priority) CSS
    DEFAULT_CSS = """
    App {
        background: $background;
        color: $text;
    }

    *:disabled {
        opacity: 0.6;
        text-opacity: 0.8;
    }
    """

    SCREENS: dict[str, Screen | Callable[[], Screen]] = {}
    _BASE_PATH: str | None = None
    CSS_PATH: CSSPathType | None = None

    TITLE: str | None = None
    """str | None: The default title for the application.

    If set to a string, this sets the default title for the application. See
    also the `title` attribute.
    """

    SUB_TITLE: str | None = None
    """str | None: The default sub-title for the application.

    If set to a string, this sets the default sub-title for the application. See
    also the `sub_title` attribute.
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
    ]

    title: Reactive[str] = Reactive("", compute=False)
    sub_title: Reactive[str] = Reactive("", compute=False)
    dark: Reactive[bool] = Reactive(True, compute=False)

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ):
        # N.B. This must be done *before* we call the parent constructor, because MessagePump's
        # constructor instantiates a `asyncio.PriorityQueue` and in Python versions older than 3.10
        # this will create some first references to an asyncio loop.
        _init_uvloop()

        super().__init__()
        self.features: frozenset[FeatureFlag] = parse_features(os.getenv("TEXTUAL", ""))

        self._filter: LineFilter | None = None
        environ = dict(os.environ)
        no_color = environ.pop("NO_COLOR", None)
        if no_color is not None:
            self._filter = Monochrome()

        self._writer_thread: _WriterThread | None = None
        if sys.__stdout__ is None:
            file = _NullFile()
        else:
            self._writer_thread = _WriterThread()
            self._writer_thread.start()
            file = self._writer_thread

        self.console = Console(
            file=file,
            markup=False,
            highlight=False,
            emoji=False,
            legacy_windows=False,
            _environ=environ,
        )
        self.error_console = Console(markup=False, stderr=True)
        self.driver_class = driver_class or self.get_driver_class()
        self._screen_stack: list[Screen] = []
        self._sync_available = False

        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None
        self._exit_renderables: list[RenderableType] = []

        self._action_targets = {"app", "screen"}
        self._animator = Animator(self)
        self._animate = self._animator.bind(self)
        self.mouse_position = Offset(0, 0)

        self.title = (
            self.TITLE if self.TITLE is not None else f"{self.__class__.__name__}"
        )
        """The title for the application.

        The initial value in a running application will be that set in `TITLE`
        (if one is set). Assign new values to this instance attribute to change
        the title.
        """

        self.sub_title = self.SUB_TITLE if self.SUB_TITLE is not None else ""
        """The sub-title for the application.

        The initial value in a running application will be that set in `SUB_TITLE`
        (if one is set). Assign new values to this instance attribute to change
        the sub-title.
        """

        self._logger = Logger(self._log)

        self._refresh_required = False

        self.design = DEFAULT_COLORS

        self.stylesheet = Stylesheet(variables=self.get_css_variables())
        self._require_stylesheet_update: set[DOMNode] = set()

        css_path = css_path or self.CSS_PATH
        if css_path is not None:
            # When value(s) are supplied for CSS_PATH, we normalise them to a list of Paths.
            css_paths: List[PurePath]
            if isinstance(css_path, str):
                css_paths = [Path(css_path)]
            elif isinstance(css_path, PurePath):
                css_paths = [css_path]
            elif isinstance(css_path, list):
                css_paths = []
                for path in css_path:
                    css_paths.append(
                        Path(path) if isinstance(path, str) else path,
                    )
            else:
                raise CssPathError(
                    "Expected a str, Path or list[str | Path] for the CSS_PATH."
                )

            # We want the CSS path to be resolved from the location of the App subclass
            css_paths = [
                _make_path_object_relative(css_path, self) for css_path in css_paths
            ]
        else:
            css_paths = []

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
        if "devtools" in self.features:
            try:
                from .devtools.client import DevtoolsClient
            except ImportError:
                # Dev dependencies not installed
                pass
            else:
                self.devtools = DevtoolsClient()

        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread_id: int = 0
        self._return_value: ReturnType | None = None
        self._exit = False

        self.css_monitor = (
            FileMonitor(self.css_path, self._on_css_change)
            if ((watch_css or self.debug) and self.css_path)
            else None
        )
        self._screenshot: str | None = None
        self._dom_lock = asyncio.Lock()
        self._dom_ready = False
        self._batch_count = 0
        self.set_class(self.dark, "-dark-mode")
        self.set_class(not self.dark, "-light-mode")

    @property
    def return_value(self) -> ReturnType | None:
        """ReturnType | None: The return type of the app."""
        return self._return_value

    @property
    def children(self) -> Sequence["Widget"]:
        """A view on to the children which contains just the screen."""
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

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation. Defaults to `value` if not set.
            duration: The duration of the animate. Defaults to None.
            speed: The speed of the animation. Defaults to None.
            delay: A delay (in seconds) before the animation starts. Defaults to 0.0.
            easing: An easing method. Defaults to "in_out_cubic".
            on_complete: A callable to invoke when the animation is finished. Defaults to None.

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

    @property
    def debug(self) -> bool:
        """Is debug mode enabled?"""
        return "debug" in self.features

    @property
    def is_headless(self) -> bool:
        """Is the driver running in 'headless' mode?"""
        return False if self._driver is None else self._driver.is_headless

    @property
    def screen_stack(self) -> list[Screen]:
        """list[Screen]: A *copy* of the screen stack."""
        return self._screen_stack.copy()

    def exit(
        self, result: ReturnType | None = None, message: RenderableType | None = None
    ) -> None:
        """Exit the app, and return the supplied result.

        Args:
            result: Return value. Defaults to None.
            message: Optional message to display on exit.
        """
        self._exit = True
        self._return_value = result
        self.post_message(messages.ExitApp())
        if message:
            self._exit_renderables.append(message)

    @property
    def focused(self) -> Widget | None:
        """Widget | None: the widget that is focused on the currently active screen."""
        return self.screen.focused

    @property
    def namespace_bindings(self) -> dict[str, tuple[DOMNode, Binding]]:
        """Get current bindings. If no widget is focused, then the app-level bindings
        are returned. If a widget is focused, then any bindings present in the active
        screen and app are merged and returned."""

        namespace_binding_map: dict[str, tuple[DOMNode, Binding]] = {}
        for namespace, bindings in reversed(self._binding_chain):
            for key, binding in bindings.keys.items():
                namespace_binding_map[key] = (namespace, binding)

        return namespace_binding_map

    def _set_active(self) -> None:
        """Set this app to be the currently active app."""
        active_app.set(self)

    def compose(self) -> ComposeResult:
        """Yield child widgets for a container."""
        yield from ()

    def get_css_variables(self) -> dict[str, str]:
        """Get a mapping of variables used to pre-populate CSS.

        Returns:
            A mapping of variable name to value.
        """
        variables = self.design["dark" if self.dark else "light"].generate()
        return variables

    def watch_dark(self, dark: bool) -> None:
        """Watches the dark bool."""
        self.set_class(dark, "-dark-mode")
        self.set_class(not dark, "-light-mode")
        try:
            self.refresh_css()
        except ScreenStackError:
            # It's possible that `dark` can be set before we have a default
            # screen, in an app's `on_load`, for example. So let's eat the
            # ScreenStackError -- the above styles will be handled once the
            # screen is spun up anyway.
            pass

    def get_driver_class(self) -> Type[Driver]:
        """Get a driver class for this platform.

        Called by the constructor.

        Returns:
            A Driver class which manages input and display.
        """

        driver_class: Type[Driver]

        driver_import = constants.DRIVER
        if driver_import is not None:
            # The driver class is set from the environment
            # Syntax should be foo.bar.baz:MyDriver
            module_import, colon, driver_symbol = driver_import.partition(":")
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
    def is_transparent(self) -> bool:
        return True

    @property
    def animator(self) -> Animator:
        return self._animator

    @property
    def screen(self) -> Screen:
        """Screen: The current screen.

        Raises:
            ScreenStackError: If there are no screens on the stack.
        """
        try:
            return self._screen_stack[-1]
        except IndexError:
            raise ScreenStackError("No screens on stack") from None

    @property
    def size(self) -> Size:
        """Size: The size of the terminal."""
        if self._driver is not None and self._driver._size is not None:
            width, height = self._driver._size
        else:
            width, height = self.console.size
        return Size(width, height)

    @property
    def log(self) -> Logger:
        """Logger: The logger object."""
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
            verbosity: Verbosity level 0-3. Defaults to 1.
        """

        devtools = self.devtools
        if devtools is None or not devtools.is_connected:
            return

        if verbosity.value > LogVerbosity.NORMAL.value and not devtools.verbose:
            return

        try:
            from .devtools.client import DevtoolsLog

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
        *args,
        **kwargs,
    ) -> CallThreadReturnType:
        """Run a callback from another thread.

        Like asyncio apps in general, Textual apps are not thread-safe. If you call methods
        or set attributes on Textual objects from a thread, you may get unpredictable results.

        This method will ensure that your code runs within the correct context.

        Args:
            callback: A callable to run.
            *args: Arguments to the callback.
            **kwargs: Keyword arguments for the callback.

        Raises:
            RuntimeError: If the app isn't running or if this method is called from the same
                thread where the app is running.
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
        """Action to toggle dark mode."""
        self.dark = not self.dark

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        """Save an SVG "screenshot". This action will save an SVG file containing the current contents of the screen.

        Args:
            filename: Filename of screenshot, or None to auto-generate. Defaults to None.
            path: Path to directory. Defaults to current working directory.
        """
        self.save_screenshot(filename, path)

    def export_screenshot(self, *, title: str | None = None) -> str:
        """Export an SVG screenshot of the current screen.

        Args:
            title: The title of the exported screenshot or None
                to use app title. Defaults to None.

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
        )
        screen_render = self.screen._compositor.render(full=True)
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
                a filename with the date and time. Defaults to None.
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
            description: Short description of action. Defaults to "".
            show: Show key in UI. Defaults to True.
            key_display: Replacement text for key, or None to use default. Defaults to None.
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
        await wait_for_idle(0)
        for key in keys:
            if key.startswith("wait:"):
                _, wait_ms = key.split(":")
                print(f"(pause {wait_ms}ms)")
                await asyncio.sleep(float(wait_ms) / 1000)
                await app._animator.wait_until_complete()
                await wait_for_idle(0)
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

    @asynccontextmanager
    async def run_test(
        self,
        *,
        headless: bool = True,
        size: tuple[int, int] | None = (80, 24),
    ):
        """An asynchronous context manager for testing app.

        Args:
            headless: Run in headless mode (no output or input). Defaults to True.
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect. Defaults to None.

        """
        from .pilot import Pilot

        app = self
        app_ready_event = asyncio.Event()

        def on_app_ready() -> None:
            """Called when app is ready to process events."""
            app_ready_event.set()

        async def run_app(app) -> None:
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
            yield Pilot(app)
        finally:
            # Shutdown the app cleanly
            await app._shutdown()
            await app_task

    async def run_async(
        self,
        *,
        headless: bool = False,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> ReturnType | None:
        """Run the app asynchronously.

        Args:
            headless: Run in headless mode (no output). Defaults to False.
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect. Defaults to None.
            auto_pilot: An auto pilot coroutine.

        Returns:
            App return value.
        """
        from .pilot import Pilot

        app = self

        auto_pilot_task: Task | None = None

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
            headless: Run in headless mode (no output). Defaults to False.
            size: Force terminal size to `(WIDTH, HEIGHT)`,
                or None to auto-detect. Defaults to None.
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
                self.log.system(
                    f"<stylesheet> loaded {len(css_paths)} CSS files in {elapsed:.0f} ms"
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
        """Shorthand for self.screen.get_child(id: str)
        Returns the first child (immediate descendent) of this DOMNode
        with the given ID.

        Args:
            id: The ID of the node to search for.
            expect_type: Require the object be of the supplied type, or None for any type.
                Defaults to None.

        Returns:
            The first child of this node with the specified ID.

        Raises:
            NoMatches: if no children could be found for this ID
            WrongType: if the wrong type was found.
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
        """Shorthand for self.screen.get_widget_by_id(id)
        Return the first descendant widget with the given ID.

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

    def update_styles(self, node: DOMNode | None = None) -> None:
        """Request update of styles.

        Should be called whenever CSS classes / pseudo classes change.

        """
        self._require_stylesheet_update.add(self.screen if node is None else node)
        self.check_idle()

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

    def _replace_screen(self, screen: Screen) -> Screen:
        """Handle the replaced screen.

        Args:
            screen: A screen object.

        Returns:
            The screen that was replaced.

        """
        screen.post_message(events.ScreenSuspend())
        self.log.system(f"{screen} SUSPENDED")
        if not self.is_screen_installed(screen) and screen not in self._screen_stack:
            screen.remove()
            self.log.system(f"{screen} REMOVED")
        return screen

    def push_screen(self, screen: Screen | str) -> AwaitMount:
        """Push a new screen on the screen stack, making it the current screen.

        Args:
            screen: A Screen instance or the name of an installed screen.

        """
        next_screen, await_mount = self._get_screen(screen)
        self._screen_stack.append(next_screen)
        self.screen.post_message(events.ScreenResume())
        self.log.system(f"{self.screen} is current (PUSHED)")
        return await_mount

    def switch_screen(self, screen: Screen | str) -> AwaitMount:
        """Switch to another screen by replacing the top of the screen stack with a new screen.

        Args:
            screen: Either a Screen object or screen name (the `name` argument when installed).

        """
        if self.screen is not screen:
            self._replace_screen(self._screen_stack.pop())
            next_screen, await_mount = self._get_screen(screen)
            self._screen_stack.append(next_screen)
            self.screen.post_message(events.ScreenResume())
            self.log.system(f"{self.screen} is current (SWITCHED)")
            return await_mount
        return AwaitMount(self.screen, [])

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
            The screen that was replaced.
        """
        screen_stack = self._screen_stack
        if len(screen_stack) <= 1:
            raise ScreenStackError(
                "Can't pop screen; there must be at least one screen on the stack"
            )
        previous_screen = self._replace_screen(screen_stack.pop())
        self.screen._screen_resized(self.size)
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
                        self.mouse_over._forward_event(events.Leave())
                    if widget is not None:
                        widget._forward_event(events.Enter())
                finally:
                    self.mouse_over = widget

    def capture_mouse(self, widget: Widget | None) -> None:
        """Send all mouse events to the given widget, disable mouse capture.

        Args:
            widget: If a widget, capture mouse event, or None to end mouse capture.
        """
        if widget == self.mouse_captured:
            return
        if self.mouse_captured is not None:
            self.mouse_captured.post_message(events.MouseRelease(self.mouse_position))
        self.mouse_captured = widget
        if widget is not None:
            widget.post_message(events.MouseCapture(self.mouse_position))

    def panic(self, *renderables: RenderableType) -> None:
        """Exits the app then displays a message.

        Args:
            *renderables: Rich renderables to display on exit.
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
            error: An exception instance.
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
        self,
        ready_callback: CallbackType | None = None,
        headless: bool = False,
        terminal_size: tuple[int, int] | None = None,
    ) -> None:
        self._set_active()

        if self.devtools is not None:
            from .devtools.client import DevtoolsConnectionError

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
            if self.css_path:
                self.stylesheet.read_all(self.css_path)
            for path, css, tie_breaker in self._get_default_css():
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
                        await self._dispatch_message(events.Mount())
                    finally:
                        self._mounted_event.set()

                    Reactive._initialize_object(self)

                    self.stylesheet.update(self)
                    self.refresh()

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
                self.console.file, self, size=terminal_size
            )

            if not self._exit:
                driver.start_application_mode()
                try:
                    if headless:
                        await run_process_messages()
                    else:
                        if self.devtools is not None:
                            devtools = self.devtools
                            assert devtools is not None
                            from .devtools.redirect_output import StdoutRedirector

                            redirector = StdoutRedirector(devtools)
                            with redirect_stderr(redirector):
                                with redirect_stdout(redirector):  # type: ignore
                                    await run_process_messages()
                        else:
                            with redirect_stderr(None):
                                with redirect_stdout(None):
                                    await run_process_messages()

                finally:
                    driver.stop_application_mode()
        except Exception as error:
            self._handle_exception(error)

    async def _pre_process(self) -> None:
        pass

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
            self.exit()

        self.set_timer(screenshot_timer, on_screenshot, name="screenshot timer")

    async def _on_compose(self) -> None:
        try:
            widgets = compose(self)
        except TypeError as error:
            raise TypeError(
                f"{self!r} compose() returned an invalid response; {error}"
            ) from error

        await self.mount_all(widgets)

    def _on_idle(self) -> None:
        """Perform actions when there are no messages in the queue."""
        if self._require_stylesheet_update and not self._batch_count:
            nodes: set[DOMNode] = {
                child
                for node in self._require_stylesheet_update
                for child in node.walk_children(with_self=True)
            }
            self._require_stylesheet_update.clear()
            self.stylesheet.update_nodes(nodes, animate=True)

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
        widget.reset_focus()
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

        # Close all screens on the stack.
        for stack_screen in reversed(self._screen_stack):
            if stack_screen._running:
                await self._prune_node(stack_screen)

        self._screen_stack.clear()

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

        if self.devtools is not None and self.devtools.is_connected:
            await self._disconnect_devtools()

        if self._writer_thread is not None:
            self._writer_thread.stop()

        self._print_error_renderables()

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
            animate: Also execute CSS animations. Defaults to True.
        """
        stylesheet = self.app.stylesheet
        stylesheet.set_variables(self.get_css_variables())
        stylesheet.reparse()
        stylesheet.update(self.app, animate=animate)
        self.screen._refresh_layout(self.size, full=True)

    def _display(self, screen: Screen, renderable: RenderableType | None) -> None:
        """Display a renderable within a sync.

        Args:
            screen: Screen instance
            renderable: A Rich renderable.
        """

        try:
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
        """Play the console 'bell'."""
        if not self.is_headless:
            self.console.bell()

    @property
    def _binding_chain(self) -> list[tuple[DOMNode, Bindings]]:
        """Get a chain of nodes and bindings to consider. If no widget is focused, returns the bindings from both the screen and the app level bindings. Otherwise, combines all the bindings from the currently focused node up the DOM to the root App.

        Returns:
            List of DOM nodes and their bindings.
        """
        focused = self.focused
        namespace_bindings: list[tuple[DOMNode, Bindings]]
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

    async def check_bindings(self, key: str, priority: bool = False) -> bool:
        """Handle a key press.

        Args:
            key: A key.
            priority: If `True` check from `App` down, otherwise from focused up.

        Returns:
            True if the key was handled by a binding, otherwise False
        """
        for namespace, bindings in (
            reversed(self._binding_chain) if priority else self._binding_chain
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
            screen = Screen(id="_default")
            self._register(self, screen)
            self._screen_stack.append(screen)
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
        """Perform an action.

        Args:
            action: Action encoded in a string.
            default_namespace: Namespace to use if not provided in the action,
                or None to use app. Defaults to None.

        Returns:
            True if the event has handled.
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
            action_target = default_namespace or self
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
        if not await self.check_bindings(key, priority=True):
            await self.check_bindings(key, priority=False)

    async def action_quit(self) -> None:
        """Quit the app as soon as possible."""
        self.exit()

    async def action_bang(self) -> None:
        1 / 0

    async def action_bell(self) -> None:
        """Play the terminal 'bell'."""
        self.bell()

    async def action_focus(self, widget_id: str) -> None:
        """Focus the given widget.

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
        """Switches to another screen.

        Args:
            screen: Name of the screen.
        """
        self.switch_screen(screen)

    async def action_push_screen(self, screen: str) -> None:
        """Pushes a screen on to the screen stack and makes it active.

        Args:
            screen: Name of the screen.
        """
        self.push_screen(screen)

    async def action_pop_screen(self) -> None:
        """Removes the topmost screen and makes the new topmost screen active."""
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

    def action_focus_next(self) -> None:
        """Focus the next widget."""
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        """Focus the previous widget."""
        self.screen.focus_previous()

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
    """Import and install the `uvloop` asyncio policy, if available.

    This is done only once, even if the function is called multiple times.

    This is provided as a nicety for users that have `uvloop` installed independently
    of Textual, as `uvloop` is not listed as a Textual dependency.
    """
    global _uvloop_init_done

    if _uvloop_init_done:
        return

    try:
        import uvloop  # type: ignore[reportMissingImports]
    except ImportError:
        pass
    else:
        uvloop.install()  # type: ignore[reportUnknownMemberType]

    _uvloop_init_done = True
