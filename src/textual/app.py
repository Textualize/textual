from __future__ import annotations

import asyncio

import logging
import signal
from typing import Any, ClassVar, Type

from rich.control import Control
from rich.repr import rich_repr, RichReprResult
from rich.screen import Screen
from rich import get_console
from rich.console import Console

from . import events
from ._context import active_app
from .driver import Driver
from ._linux_driver import LinuxDriver
from .message_pump import MessagePump
from .view import View, LayoutView

log = logging.getLogger("rich")


LayoutDefinition = dict[str, Any]

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


@rich_repr
class App(MessagePump):
    view: View

    KEYS: ClassVar[dict[str, str]] = {}

    def __init__(
        self,
        console: Console = None,
        screen: bool = True,
        driver: Type[Driver] = None,
        view: View = None,
        title: str = "Megasoma Application",
    ):
        super().__init__()
        self.console = console or get_console()
        self._screen = screen
        self.driver = driver or LinuxDriver
        self.title = title
        self.view = view or LayoutView()
        self.children: set[MessagePump] = set()

    def __rich_repr__(self) -> RichReprResult:
        yield "title", self.title

    @classmethod
    def run(
        cls, console: Console = None, screen: bool = True, driver: Type[Driver] = None
    ):
        async def run_app() -> None:
            app = cls(console=console, screen=screen, driver=driver)
            await app.process_messages()

        asyncio.run(run_app())

    def on_keyboard_interupt(self) -> None:
        loop = asyncio.get_event_loop()
        event = events.ShutdownRequest(sender=self)
        asyncio.run_coroutine_threadsafe(self.post_message(event), loop=loop)

    async def process_messages(self) -> None:
        log.debug("driver=%r", self.driver)
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGINT, self.on_keyboard_interupt)
        driver = self.driver(self.console, self)
        try:
            driver.start_application_mode()
        except Exception:
            log.exception("error starting application mode")
            raise

        active_app.set(self)

        await self.add(self.view)

        await self.post_message(events.Startup(sender=self))
        self.refresh()
        try:
            await super().process_messages()
        finally:
            loop.remove_signal_handler(signal.SIGINT)
            driver.stop_application_mode()

        await asyncio.gather(*(child.close_messages() for child in self.children))
        self.children.clear()

    async def add(self, child: MessagePump) -> None:
        self.children.add(child)
        asyncio.create_task(child.process_messages())
        await child.post_message(events.Created(sender=self))

    def refresh(self) -> None:
        console = self.console
        with console:
            console.print(
                Screen(Control.home(), self.view, Control.home(), application_mode=True)
            )

    async def on_event(self, event: events.Event, priority: int) -> None:
        if isinstance(event, events.Key):
            key_action = self.KEYS.get(event.key, None)
            if key_action is not None:
                log.debug("action %r", key_action)
                await self.action(key_action)
                return

        if isinstance(event, events.InputEvent):
            await self.view.forward_input_event(event)
        else:
            await super().on_event(event, priority)

    async def on_idle(self, event: events.Idle) -> None:
        await self.view.post_message(event)

    async def action(self, action: str) -> None:
        if "." in action:
            destination, action_name, *tokens = action.split(".")
        else:
            destination = "app"
            action_name = action
            tokens = []

        if destination == "app":
            method_name = f"action_{action_name}"
            method = getattr(self, method_name, None)
            if method is not None:
                await method(tokens)

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

    async def action_quit(self, tokens: list[str]) -> None:
        await self.close_messages()


if __name__ == "__main__":
    import asyncio
    from logging import FileHandler

    from .widgets.header import Header
    from .widgets.window import Window
    from .widgets.placeholder import Placeholder

    from rich.markdown import Markdown

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[FileHandler("richtui.log")],
    )

    with open("richreadme.md", "rt") as fh:
        readme = Markdown(fh.read(), hyperlinks=True, code_theme="fruity")

    from rich import print

    class MyApp(App):

        KEYS = {"q": "quit", "ctrl+c": "quit"}

        async def on_startup(self, event: events.Startup) -> None:
            await self.view.mount_all(
                header=Header(self.title), left=Placeholder(), body=Window(readme)
            )

    MyApp.run()
