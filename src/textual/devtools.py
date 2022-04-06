from __future__ import annotations

import asyncio
import base64
import json
import pickle
import sys
import weakref
from asyncio import Queue, CancelledError
from contextlib import suppress
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import cast, Iterable, Literal

from aiohttp import WSMessage, WSMsgType, WSCloseCode
from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_routedef import get
from aiohttp.web_ws import WebSocketResponse
from dateutil.tz import tz
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.rule import Rule
from rich.segment import Segments, Segment
from rich.table import Table

DEFAULT_PORT = 8081
DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS = 2
QUEUEABLE_TYPES = {"client_log", "client_spillover"}


class DevtoolsLogMessage:
    def __init__(
        self,
        segments: Iterable[Segment],
        path: str,
        line_number: int,
        unix_timestamp: int,
    ):
        self.segments = segments
        self.path = path
        self.line_number = line_number
        self.unix_timestamp = unix_timestamp

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        local_time = (
            datetime.fromtimestamp(self.unix_timestamp)
            .replace(tzinfo=timezone.utc)
            .astimezone(tz=tz.tzlocal())
        )
        timezone_name = local_time.tzname()
        table = Table.grid(expand=True)
        table.add_column()
        table.add_column()
        file_link = f"file://{Path(self.path).absolute()}"
        file_and_line = f"{Path(self.path).name}:{self.line_number}"
        table.add_row(
            f" [#888177]{local_time.time()} [dim]{timezone_name}[/]",
            Align.right(f"[#888177][link={file_link}]{file_and_line} "),
            style="on #292724",
        )
        yield table
        yield Segments(self.segments)


DevtoolsMessageLevel = Literal["info", "warning", "error"]


class DevtoolsInternalMessage:
    def __init__(self, message: str, *, level: str = "info"):
        self.message = message
        self.level = level

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        level_to_style = {
            "info": "dim",
            "warning": "#FFA000",
            "error": "#C52828",
        }
        yield Rule(self.message, style=level_to_style.get(self.level, "dim"))


async def _enqueue_size_changes(
    console: Console, outgoing_queue: Queue, poll_delay: int
):
    current_width = console.width
    current_height = console.height
    while True:
        width = console.width
        height = console.height
        dimensions_changed = width != current_width or height != current_height
        if dimensions_changed:
            await _enqueue_server_info(outgoing_queue, width, height)
            current_width = width
            current_height = height
        await asyncio.sleep(poll_delay)


async def _enqueue_server_info(outgoing_queue: Queue, width: int, height: int) -> None:
    await outgoing_queue.put(
        {
            "type": "server_info",
            "payload": {
                "width": width,
                "height": height,
            },
        }
    )


async def _consume_incoming(console: Console, incoming_queue: Queue[dict]) -> None:
    while True:
        message_json = await incoming_queue.get()
        type = message_json["type"]

        if type == "client_log":
            path = message_json["payload"]["path"]
            line_number = message_json["payload"]["line_number"]
            timestamp = message_json["payload"]["timestamp"]
            encoded_segments = message_json["payload"]["encoded_segments"]
            decoded_segments = base64.b64decode(encoded_segments)
            segments = pickle.loads(decoded_segments)

            log_message = DevtoolsLogMessage(
                segments=segments,
                path=path,
                line_number=line_number,
                unix_timestamp=timestamp,
            )
            console.print(log_message)
        elif type == "client_spillover":
            spillover = int(message_json["payload"]["spillover"])
            info_renderable = DevtoolsInternalMessage(
                f"Discarded {spillover} messages", level="warning"
            )
            console.print(info_renderable)
        incoming_queue.task_done()


async def _consume_outgoing(
    outgoing_queue: Queue[dict], websocket: WebSocketResponse
) -> None:
    while True:
        message_json = await outgoing_queue.get()
        type = message_json["type"]
        if type == "server_info":
            await websocket.send_json(message_json)


async def websocket_handler(request: Request):
    websocket = WebSocketResponse()
    await websocket.prepare(request)
    request.app["websockets"].add(websocket)

    console = request.app["console"]
    size_change_poll_delay = request.app["size_change_poll_delay_secs"]

    incoming_queue: Queue[dict] = Queue()
    outgoing_queue: Queue[dict] = Queue()

    request.app["tasks"].extend(
        (
            asyncio.create_task(_consume_outgoing(outgoing_queue, websocket)),
            asyncio.create_task(
                _enqueue_size_changes(
                    console, outgoing_queue, poll_delay=size_change_poll_delay
                )
            ),
            asyncio.create_task(_consume_incoming(console, incoming_queue)),
        )
    )

    console.print(
        DevtoolsInternalMessage(f"Client '{escape(request.remote)}' connected")
    )

    await _enqueue_server_info(
        outgoing_queue, width=console.width, height=console.height
    )
    try:
        async for message in websocket:
            message = cast(WSMessage, message)
            if message.type == WSMsgType.TEXT:
                try:
                    message_json = json.loads(message.data)
                except JSONDecodeError:
                    console.print(escape(str(message.data)))
                    continue

                type = message_json.get("type")
                if not type:
                    continue
                if type in QUEUEABLE_TYPES:
                    await incoming_queue.put(message_json)
            elif message.type == WSMsgType.ERROR:
                console.print(
                    DevtoolsInternalMessage("Websocket error occurred", level="error")
                )
                break
    except Exception as error:
        console.print(DevtoolsInternalMessage(str(error), level="error"))
    finally:
        request.app["websockets"].discard(websocket)
        console.print()
        console.print(
            DevtoolsInternalMessage(f"Client '{escape(request.remote)}' disconnected")
        )

    return websocket


async def _on_shutdown(app: Application) -> None:
    for task in app["tasks"]:
        task.cancel()
        with suppress(CancelledError):
            await task

    for websocket in set(app["websockets"]):
        await websocket.close(
            code=WSCloseCode.GOING_AWAY, message="Shutting down server"
        )


def _run_devtools(port: int) -> None:
    app = _make_devtools_aiohttp_app()
    run_app(app, port=port)


def _make_devtools_aiohttp_app(
    size_change_poll_delay_secs: float = DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS,
):
    app = Application()
    app["size_change_poll_delay_secs"] = size_change_poll_delay_secs
    app["console"] = Console()
    app["websockets"] = weakref.WeakSet()
    app["tasks"] = []
    app.add_routes(
        [
            get("/textual-devtools-websocket", websocket_handler),
        ]
    )
    app.on_shutdown.append(_on_shutdown)
    return app


if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = DEFAULT_PORT
    _run_devtools(port)
