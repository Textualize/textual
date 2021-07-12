from __future__ import annotations
import os

import asyncio
from functools import partial
import logging
import signal
from typing import Any, Callable, ClassVar, Type, TypeVar
import warnings

from rich.control import Control
import rich.repr
from rich.screen import Screen
from rich import get_console
from rich.console import Console, RenderableType
from rich.style import Style
from rich.traceback import Traceback

from . import events
from . import actions
from ._animator import Animator
from .binding import Bindings, NoBinding
from .geometry import Point, Region
from ._context import active_app
from ._event_broker import extract_handler_actions, NoHandler
from .keys import Binding
from .driver import Driver
from .layouts.dock import DockLayout, Dock
from ._linux_driver import LinuxDriver
from .message_pump import MessagePump
from .message import Message
from .view import View
from .views import DockView
from .widget import Widget, Widget, Reactive

log = logging.getLogger("rich")


# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)
# https://github.com/boto/boto3/issues/454
# warnings.filterwarnings(
#     "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
# )


LayoutDefinition = "dict[str, Any]"

ViewType = TypeVar("ViewType", bound=View)

# try:
#     import uvloop
# except ImportError:
#     pass
# else:
#     uvloop.install()


class ActionError(Exception):
    pass


class ShutdownError(Exception):
    pass


@rich.repr.auto
class App(MessagePump):

    KEYS: ClassVar[dict[str, str]] = {}

    def __init__(
        self,
        console: Console = None,
        screen: bool = True,
        driver_class: Type[Driver] = None,
        title: str = "Textual Application",
    ):
        self.console = console or get_console()
        self._screen = screen
        self.driver_class = driver_class or LinuxDriver
        self._title = title
        self._layout = DockLayout()
        self._view_stack: list[View] = []
        self.children: set[MessagePump] = set()

        self.focused: Widget | None = None
        self.mouse_over: Widget | None = None
        self.mouse_captured: Widget | None = None
        self._driver: Driver | None = None

        self._docks: list[Dock] = []
        self._action_targets = {"app", "view"}
        self._animator = Animator(self)
        self.animate = self._animator.bind(self)
        self.mouse_position = Point(0, 0)
        self.bindings = Bindings()
        self._title = title

        self.bindings.bind("ctrl+c", "quit")

        super().__init__()

    title: Reactive[str] = Reactive("Textual")
    sub_title: Reactive[str] = Reactive("")

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "title", self.title

    def __rich__(self) -> RenderableType:
        return self.view

    @property
    def animator(self) -> Animator:
        return self._animator

    @property
    def view(self) -> View:
        return self._view_stack[-1]

    async def bind(
        self, keys: str, action: str, description: str = "", show: bool = False
    ) -> None:
        self.bindings.bind(keys, action, description, show=show)

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
            app = cls(console=console, screen=screen, driver_class=driver, **kwargs)
            await app.process_messages()

        asyncio.run(run_app())

    async def push_view(self, view: ViewType) -> ViewType:
        await self.register(view)
        view.set_parent(self)
        self._view_stack.append(view)
        return view

    def on_keyboard_interupt(self) -> None:
        loop = asyncio.get_event_loop()
        event = events.ShutdownRequest(sender=self)
        asyncio.run_coroutine_threadsafe(self.post_message(event), loop=loop)

    async def set_focus(self, widget: Widget | None) -> None:
        log.debug("set_focus %r", widget)
        if widget == self.focused:
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
        """Send all Mouse events to a given widget."""
        if widget == self.mouse_captured:
            return
        if self.mouse_captured is not None:
            await self.mouse_captured.post_message(
                events.MouseReleased(self, self.mouse_position)
            )
        self.mouse_captured = widget
        if widget is not None:
            await widget.post_message(events.MouseCaptured(self, self.mouse_position))

    async def process_messages(self) -> None:
        log.debug("driver=%r", self.driver_class)
        # loop = asyncio.get_event_loop()
        # loop.add_signal_handler(signal.SIGINT, self.on_keyboard_interupt)
        driver = self._driver = self.driver_class(self.console, self)
        active_app.set(self)

        await self.push_view(View())

        self.view.set_parent(self)
        await self.register(self.view)

        await self.dispatch_message(events.Load(sender=self))

        try:
            driver.start_application_mode()
        except Exception:
            self.console.print_exception()
            log.exception("error starting application mode")
        else:
            traceback: Traceback | None = None

            try:
                self.title = self._title
                await self.post_message(events.Startup(sender=self))
                self.require_layout()
                await self.animator.start()

                await super().process_messages()
                await self.animator.stop()

                while self.children:
                    child = self.children.pop()
                    log.debug("closing %r", child)
                    await child.close_messages()

                while self._view_stack:
                    view = self._view_stack.pop()
                    await view.close_messages()
            except Exception:
                traceback = Traceback(show_locals=True)
            finally:
                driver.stop_application_mode()
                if traceback is not None:
                    self.console.print(traceback)

    def require_repaint(self) -> None:
        self.refresh()

    def require_layout(self) -> None:
        self.view.require_layout()

    async def call_later(self, callback: Callable, *args, **kwargs) -> None:
        await self.post_message(events.Idle(self))
        await self.post_message(
            events.Callback(self, partial(callback, *args, **kwargs))
        )

    async def message_update(self, message: Message) -> None:
        self.refresh()

    async def register(self, child: MessagePump) -> None:
        self.children.add(child)
        child.start_messages()
        await child.post_message(events.Created(sender=self))

    async def remove(self, child: MessagePump) -> None:
        self.children.remove(child)

    async def shutdown(self):
        driver = self._driver
        assert driver is not None
        driver.disable_input()
        await self.close_messages()

    def refresh(self) -> None:
        sync_available = os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal"
        if not self._closed:
            console = self.console
            try:
                if sync_available:
                    console.file.write("\x1bP=1s\x1b\\")
                with console:
                    console.print(Screen(Control.home(), self.view, Control.home()))
                if sync_available:
                    console.file.write("\x1bP=2s\x1b\\")
            except Exception:
                log.exception("refresh failed")

    def display(self, renderable: RenderableType) -> None:
        if not self._closed:
            console = self.console
            try:
                with console:
                    console.print(renderable)
            except Exception:
                log.exception("display failed")

    def get_widget_at(self, x: int, y: int) -> tuple[Widget, Region]:
        return self.view.get_widget_at(x, y)

    async def on_event(self, event: events.Event) -> None:
        if isinstance(event, events.Key):
            try:
                binding = self.bindings.get_key(event.key)
            except NoBinding:
                pass
            else:
                await self.action(binding.action)
                return

        if isinstance(event, events.InputEvent):
            if isinstance(event, events.MouseEvent):
                self.mouse_position = Point(event.x, event.y)
            if isinstance(event, events.Key) and self.focused is not None:
                await self.focused.forward_event(event)
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
                raise ActionError("Action namespace {destination} is not known")
            action_target = getattr(self, destination)
        else:
            action_target = default_namespace or self
            action_name = action

        log.debug("ACTION %r %r", action_target, action_name)
        await self.dispatch_action(action_target, action_name, params)

    async def dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> None:
        _rich_traceback_guard = True
        method_name = f"action_{action_name}"
        method = getattr(namespace, method_name, None)
        if method is not None:
            await method(*params)

    async def broker_event(
        self, event_name: str, event: events.Event, default_namespace: object | None
    ) -> bool:
        try:
            style = getattr(event, "style")
        except AttributeError:
            return False
        try:
            modifiers, action = extract_handler_actions(event_name, style.meta)
        except NoHandler:
            return False
        await self.action(
            action, default_namespace=default_namespace, modifiers=modifiers
        )
        return True

    async def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log.debug("shutdown request")
        await self.close_messages()

    async def on_resize(self, event: events.Resize) -> None:
        await self.view.post_message(event)

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

    # from rich.console import Console

    # console = Console()
    # console.print(scroll_bar, height=10)
    # console.print(scroll_view, height=20)

    # import sys

    # sys.exit()

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[FileHandler("richtui.log")],
    )

    class MyApp(App):
        """Just a test app."""

        async def on_load(self, event: events.Load) -> None:
            await self.bind("q,ctrl+c", "quit")
            await self.bind("x", "bang")
            await self.bind("b", "toggle_sidebar")

        show_bar: Reactive[bool] = Reactive(False)

        async def watch_show_bar(self, show_bar: bool) -> None:
            self.animator.animate(self.bar, "layout_offset_x", -40 if show_bar else 0)

        async def action_toggle_sidebar(self) -> None:
            self.show_bar = not self.show_bar

        async def on_startup(self, event: events.Startup) -> None:

            view = await self.push_view(DockView())

            header = Header()
            footer = Footer()
            self.bar = Placeholder(name="left")
            footer.add_key("b", "Toggle sidebar")
            footer.add_key("q", "Quit")

            await view.dock(header, edge="top")
            await view.dock(footer, edge="bottom")
            await view.dock(self.bar, edge="left", size=40, z=1)

            # await view.dock(Placeholder(), Placeholder(), edge="top")

            sub_view = DockView()
            await sub_view.dock(Placeholder(), Placeholder(), edge="top")
            await view.dock(sub_view, edge="left")

            # self.refresh()

            # footer = Footer()
            # footer.add_key("b", "Toggle sidebar")
            # footer.add_key("q", "Quit")

            # readme_path = os.path.join(
            #     os.path.dirname(os.path.abspath(__file__)), "richreadme.md"
            # )
            # # scroll_view = LayoutView()
            # # scroll_bar = ScrollBar()
            # with open(readme_path, "rt") as fh:
            #     readme = Markdown(fh.read(), hyperlinks=True, code_theme="fruity")
            # # scroll_view.layout.split_column(
            # #     Layout(readme, ratio=1), Layout(scroll_bar, ratio=2, size=2)
            # # )
            # layout = Layout()
            # layout.split_column(Layout(name="l1"), Layout(name="l2"))
            # # sub_view = LayoutView(name="Sub view", layout=layout)

            # sub_view = ScrollView(readme)

            # # await sub_view.mount_all(l1=Placeholder(), l2=Placeholder())

            # await self.view.mount_all(
            #     header=Header(self.title),
            #     left=Placeholder(),
            #     body=sub_view,
            #     footer=footer,
            # )

    # app = MyApp()
    # from rich.console import Console

    # console = Console()
    # console.print(app._view_stack[0], height=30)
    # console.print(app._view_stack)
    MyApp.run()
