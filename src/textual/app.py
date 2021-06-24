from __future__ import annotations
from argparse import Action

import asyncio

import logging
import signal
from typing import Any, ClassVar, Type
import warnings

from rich.control import Control
from rich.layout import Layout
import rich.repr
from rich.screen import Screen
from rich import get_console
from rich.console import Console, RenderableType
from rich.traceback import Traceback

from . import events
from . import actions
from ._animator import Animator
from ._context import active_app
from .driver import Driver
from ._linux_driver import LinuxDriver
from .message_pump import MessagePump
from .view import View, LayoutView
from .widget import Widget, WidgetBase

log = logging.getLogger("rich")


# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)
# https://github.com/boto/boto3/issues/454
# warnings.filterwarnings(
#     "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
# )


LayoutDefinition = "dict[str, Any]"

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
    view: View

    KEYS: ClassVar[dict[str, str]] = {}

    def __init__(
        self,
        console: Console = None,
        screen: bool = True,
        driver_class: Type[Driver] = None,
        view: View = None,
        title: str = "Megasoma Application",
    ):
        super().__init__()
        self.console = console or get_console()
        self._screen = screen
        self.driver_class = driver_class or LinuxDriver
        self.title = title
        self.view = view or self.create_default_view()
        self.children: set[MessagePump] = set()

        self.focused: WidgetBase | None = None
        self.mouse_over: WidgetBase | None = None
        self._driver: Driver | None = None

        self._action_targets = {"app": self, "view": self.view}
        self._animator = Animator(self)

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "title", self.title

    def __rich__(self) -> RenderableType:
        return self.view

    @property
    def animator(self) -> Animator:
        return self._animator

    @classmethod
    def run(
        cls, console: Console = None, screen: bool = True, driver: Type[Driver] = None
    ):
        """Run the app.

        Args:
            console (Console, optional): Console object. Defaults to None.
            screen (bool, optional): Enable application mode. Defaults to True.
            driver (Type[Driver], optional): Driver class or None for default. Defaults to None.
        """

        async def run_app() -> None:
            app = cls(console=console, screen=screen, driver_class=driver)

            await app.process_messages()

        asyncio.run(run_app())

    def create_default_view(self) -> View:
        """Create the default view."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3, ratio=0),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=1, ratio=0),
        )
        layout["main"].split_row(
            Layout(name="left", size=30, visible=True),
            Layout(name="body", ratio=1),
            Layout(name="right", size=30, visible=False),
        )
        view = LayoutView(layout=layout)
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

    async def set_mouse_over(self, widget: WidgetBase | None) -> None:
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

    async def process_messages(self) -> None:
        log.debug("driver=%r", self.driver_class)
        # loop = asyncio.get_event_loop()
        # loop.add_signal_handler(signal.SIGINT, self.on_keyboard_interupt)
        driver = self._driver = self.driver_class(self.console, self)
        active_app.set(self)
        self.view.set_parent(self)
        await self.add(self.view)

        await self.post_message(events.Startup(sender=self))

        try:
            driver.start_application_mode()
        except Exception:
            self.console.print_exception()
            log.exception("error starting application mode")
        else:
            traceback: Traceback | None = None
            await self.animator.start()
            try:
                await super().process_messages()
            except Exception:
                traceback = Traceback(show_locals=True)

            await self.animator.stop()
            await self.view.close_messages()
            driver.stop_application_mode()
            if traceback is not None:
                self.console.print(traceback)

    async def add(self, child: MessagePump) -> None:
        self.children.add(child)
        child.start_messages()
        await child.post_message(events.Created(sender=self))

    async def remove(self, child: MessagePump) -> None:
        self.children.remove(child)

    async def shutdown(self):
        driver = self._driver
        driver.disable_input()
        await self.close_messages()

    def refresh(self) -> None:
        if not self._closed:
            console = self.console
            try:
                with console:
                    console.print(Screen(Control.home(), self.view, Control.home()))
            except Exception:
                log.exception("refresh failed")

    async def on_event(self, event: events.Event) -> None:
        if isinstance(event, events.Key):
            key_action = self.KEYS.get(event.key, None)
            if key_action is not None:
                await self.action(key_action)
                return

        if isinstance(event, events.InputEvent):
            if isinstance(event, events.Key) and self.focused is not None:
                await self.focused.forward_event(event)
            await self.view.forward_event(event)
        else:
            await super().on_event(event)

    async def action(
        self, action: str, default_namespace: object | None = None
    ) -> None:
        """Perform an action.

        Args:
            action (str): Action encoded in a string.
        """
        default_target = default_namespace or self
        target, params = actions.parse(action)
        if "." in target:
            destination, action_name = target.split(".", 1)
            action_target = self._action_targets.get(destination, None)
            if action_target is None:
                raise ActionError("Action namespace {destination} is not known")
        else:
            action_target = default_namespace or self
            action_name = action

        log.debug("ACTION %r %r", action_target, action_name)
        await self.dispatch_action(action_target, action_name, params)

    async def dispatch_action(
        self, namespace: object, action_name: str, params: Any
    ) -> None:
        method_name = f"action_{action_name}"
        method = getattr(namespace, method_name, None)
        if method is not None:
            await method(*params)

    async def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        log.debug("shutdown request")
        await self.close_messages()

    async def on_resize(self, event: events.Resize) -> None:
        await self.view.post_message(event)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.view.post_message(event)

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        await self.view.post_message(event)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        await self.view.post_message(event)

    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        await self.view.post_message(event)

    async def on_mouse_scroll_down(self, event: events.MouseScrollUp) -> None:
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

    from .widgets.header import Header
    from .widgets.footer import Footer

    from .widgets.placeholder import Placeholder
    from .scrollbar import ScrollBar

    from rich.markdown import Markdown

    from .widgets.scroll_view import ScrollView

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

        KEYS = {"q": "quit", "x": "bang", "ctrl+c": "quit", "b": "view.toggle('left')"}

        async def on_startup(self, event: events.Startup) -> None:
            footer = Footer()
            footer.add_key("b", "Toggle sidebar")
            footer.add_key("q", "Quit")

            readme_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "richreadme.md"
            )
            # scroll_view = LayoutView()
            # scroll_bar = ScrollBar()
            with open(readme_path, "rt") as fh:
                readme = Markdown(fh.read(), hyperlinks=True, code_theme="fruity")
            # scroll_view.layout.split_column(
            #     Layout(readme, ratio=1), Layout(scroll_bar, ratio=2, size=2)
            # )
            layout = Layout()
            layout.split_column(Layout(name="l1"), Layout(name="l2"))
            # sub_view = LayoutView(name="Sub view", layout=layout)

            sub_view = ScrollView(readme)

            # await sub_view.mount_all(l1=Placeholder(), l2=Placeholder())

            await self.view.mount_all(
                header=Header(self.title),
                left=Placeholder(),
                body=sub_view,
                footer=footer,
            )

    # app = MyApp()
    # from rich.console import Console

    # console = Console()
    # console.print(app, height=30)
    MyApp.run()
