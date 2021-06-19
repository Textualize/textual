from __future__ import annotations

import asyncio

import logging
import signal
from typing import Any, ClassVar, Type
import warnings

from rich.control import Control
from rich.repr import rich_repr, RichReprResult
from rich.screen import Screen
from rich import get_console
from rich.console import Console

from . import events
from . import actions
from ._context import active_app
from .driver import Driver
from ._linux_driver import LinuxDriver
from .message_pump import MessagePump
from .view import View, LayoutView

log = logging.getLogger("rich")


# asyncio will warn against resources not being cleared
warnings.simplefilter("always", ResourceWarning)
# https://github.com/boto/boto3/issues/454
warnings.filterwarnings(
    "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
)


LayoutDefinition = "dict[str, Any]"

# try:
#     import uvloop
# except ImportError:
#     pass
# else:
#     uvloop.install()


class ShutdownError(Exception):
    pass


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

        self._action_targets = {"app": self, "view": self.view}

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
        try:
            await self._process_messages()
        except Exception:
            self.console.print_exception(show_locals=True)

    async def _process_messages(self) -> None:
        log.debug("driver=%r", self.driver)
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGINT, self.on_keyboard_interupt)
        driver = self.driver(self.console, self)

        active_app.set(self)

        await self.add(self.view)

        await self.post_message(events.Startup(sender=self))

        try:
            driver.start_application_mode()
        except Exception:
            log.exception("error starting application mode")
            raise
        try:
            await super().process_messages()
        finally:
            try:
                if self.children:

                    async def close_all() -> None:
                        for child in self.children:
                            await child.close_messages()
                        await asyncio.gather(*(child.task for child in self.children))

                    try:
                        await asyncio.wait_for(close_all(), timeout=5)
                    except asyncio.TimeoutError as error:
                        raise ShutdownError(
                            "Timeout closing messages pump(s)"
                        ) from None

                self.children.clear()
            finally:
                try:
                    driver.stop_application_mode()
                finally:
                    loop.remove_signal_handler(signal.SIGINT)

    async def add(self, child: MessagePump) -> None:
        self.children.add(child)
        child.start_messages()
        await child.post_message(events.Created(sender=self))

    def refresh(self) -> None:
        console = self.console
        try:
            with console:
                console.print(Screen(Control.home(), self.view, Control.home()))
        except Exception:
            log.exception("refresh failed")

    async def on_event(self, event: events.Event, priority: int) -> None:
        if isinstance(event, events.Key):
            key_action = self.KEYS.get(event.key, None)
            if key_action is not None:
                await self.action(key_action)
                return

        if isinstance(event, events.InputEvent):
            await self.view.forward_input_event(event)
        else:
            await super().on_event(event, priority)

    async def on_idle(self, event: events.Idle) -> None:
        await self.view.post_message(event)

    async def action(self, action: str) -> None:
        """Perform an action.

        Args:
            action (str): Action encoded in a string.
        """

        target, params = actions.parse(action)
        if "." in target:
            destination, action_name = target.split(".", 1)
        else:
            destination = "app"
            action_name = action

        log.debug("ACTION %r %r", destination, action_name)
        await self.dispatch_action(destination, action_name, params)

    async def dispatch_action(
        self, destination: str, action_name: str, params: Any
    ) -> None:
        action_target = self._action_targets.get(destination, None)
        if action_target is not None:
            method_name = f"action_{action_name}"
            method = getattr(action_target, method_name, None)
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
        await self.close_messages()

    async def action_bang(self) -> None:
        1 / 0


if __name__ == "__main__":
    import asyncio
    from logging import FileHandler

    from .widgets.header import Header
    from .widgets.footer import Footer
    from .widgets.window import Window
    from .widgets.placeholder import Placeholder

    from rich.markdown import Markdown

    import os

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

            with open(readme_path, "rt") as fh:
                readme = Markdown(fh.read(), hyperlinks=True, code_theme="fruity")

            await self.view.mount_all(
                header=Header(self.title),
                left=Placeholder(),
                body=Window(readme),
                footer=footer,
            )

    MyApp.run()
