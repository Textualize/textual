from __future__ import annotations

import asyncio
import base64
import json
import pickle
import sys
import weakref
from asyncio import Queue, Task
from json import JSONDecodeError
from typing import cast

from textual.devtools.client import DEFAULT_PORT
from textual.devtools.renderables import DevtoolsLogMessage, DevtoolsInternalMessage


from aiohttp import WSMessage, WSMsgType, WSCloseCode
from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_routedef import get
from aiohttp.web_ws import WebSocketResponse
from rich.console import Console
from rich.markup import escape


DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS = 2
QUEUEABLE_TYPES = {"client_log", "client_spillover"}


async def _enqueue_size_changes(
    console: Console,
    outgoing_queue: Queue[dict | None],
    poll_delay: int,
    shutdown_event: asyncio.Event,
) -> None:
    """Poll console dimensions, and add a `server_info` message to the Queue
    any time a change occurs

    Args:
        console (Console): The Console instance to poll for size changes on
        outgoing_queue (Queue): The Queue to add to when a size change occurs
        poll_delay (int): Time between polls
        shutdown_event (asyncio.Event): When set, this coroutine will stop polling
            and will eventually return (after the current poll completes)
    """
    current_width = console.width
    current_height = console.height
    while not shutdown_event.is_set():
        width = console.width
        height = console.height
        dimensions_changed = width != current_width or height != current_height
        if dimensions_changed:
            await _enqueue_server_info(outgoing_queue, width, height)
            current_width = width
            current_height = height
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=poll_delay)
        except asyncio.TimeoutError:
            pass


async def _enqueue_server_info(
    outgoing_queue: Queue[dict | None], width: int, height: int
) -> None:
    """Add `server_info` message to the queue

    Args:
        outgoing_queue (Queue[dict | None]): The Queue to add the message to
        width (int): The new width of the server Console
        height (int): The new height of the server Console
    """
    await outgoing_queue.put(
        {
            "type": "server_info",
            "payload": {
                "width": width,
                "height": height,
            },
        }
    )


async def _consume_incoming(
    console: Console, incoming_queue: Queue[dict | None]
) -> None:
    """Consume messages from the incoming (client -> server) Queue, and print
    the corresponding renderables to the console for each message.

    Args:
        console (Console): The Console instance to print to
        incoming_queue (Queue[dict | None]): The Queue containing messages to process
    """
    while True:
        message_json = await incoming_queue.get()
        if message_json is None:
            incoming_queue.task_done()
            break

        type = message_json["type"]
        if type == "client_log":
            path = message_json["payload"]["path"]
            line_number = message_json["payload"]["line_number"]
            timestamp = message_json["payload"]["timestamp"]
            encoded_segments = message_json["payload"]["encoded_segments"]
            decoded_segments = base64.b64decode(encoded_segments)
            segments = pickle.loads(decoded_segments)
            console.print(
                DevtoolsLogMessage(
                    segments=segments,
                    path=path,
                    line_number=line_number,
                    unix_timestamp=timestamp,
                )
            )
        elif type == "client_spillover":
            spillover = int(message_json["payload"]["spillover"])
            info_renderable = DevtoolsInternalMessage(
                f"Discarded {spillover} messages", level="warning"
            )
            console.print(info_renderable)
        incoming_queue.task_done()


async def _consume_outgoing(
    outgoing_queue: Queue[dict | None], websocket: WebSocketResponse
) -> None:
    """Consume messages from the outgoing (server -> client) Queue.

    Args:
        outgoing_queue (Queue[dict | None]): The queue to consume from
        websocket (WebSocketResponse): The websocket to write to
    """
    while True:
        message_json = await outgoing_queue.get()
        if message_json is None:
            outgoing_queue.task_done()
            break
        type = message_json["type"]
        if type == "server_info":
            await websocket.send_json(message_json)
        outgoing_queue.task_done()


async def websocket_handler(request: Request) -> WebSocketResponse:
    """aiohttp websocket handler for sending data between devtools client and server

    Args:
        request (Request): The request to the websocket endpoint

    Returns:
        WebSocketResponse: The websocket response
    """
    websocket = WebSocketResponse()
    await websocket.prepare(request)
    request.app["websockets"].add(websocket)

    console = request.app["console"]

    size_change_poll_delay = request.app["size_change_poll_delay_secs"]
    shutdown_event: asyncio.Event = request.app["shutdown_event"]

    outgoing_queue: Queue[dict | None] = request.app["outgoing_queue"]
    incoming_queue: Queue[dict | None] = request.app["incoming_queue"]

    size_change_task = asyncio.create_task(
        _enqueue_size_changes(
            console,
            outgoing_queue,
            poll_delay=size_change_poll_delay,
            shutdown_event=shutdown_event,
        )
    )
    consume_outgoing_task = asyncio.create_task(
        _consume_outgoing(outgoing_queue, websocket)
    )
    consume_incoming_task = asyncio.create_task(
        _consume_incoming(console, incoming_queue)
    )

    request.app["tasks"].update(
        {
            "consume_incoming_task": consume_incoming_task,
            "consume_outgoing_task": consume_outgoing_task,
            "size_change_task": size_change_task,
        }
    )

    if request.remote:
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
                if type in QUEUEABLE_TYPES and not shutdown_event.is_set():
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
        if request.remote:
            console.print(
                DevtoolsInternalMessage(
                    f"Client '{escape(request.remote)}' disconnected"
                )
            )

    return websocket


async def _on_shutdown(app: Application) -> None:
    """aiohttp shutdown handler, called when the aiohttp server is stopped"""
    tasks: dict[str, Task] = app["tasks"]

    # Close the websockets to stop most writes to the incoming queue
    for websocket in set(app["websockets"]):
        await websocket.close(
            code=WSCloseCode.GOING_AWAY, message="Shutting down server"
        )

    # This task needs to shut down first as it writes to the outgoing queue
    shutdown_event: asyncio.Event = app["shutdown_event"]
    shutdown_event.set()
    size_change_task = tasks.get("size_change_task")
    if size_change_task:
        await size_change_task

    # Now stop the tasks which read from the queues
    incoming_queue: Queue[dict | None] = app["incoming_queue"]
    await incoming_queue.put(None)

    outgoing_queue: Queue[dict | None] = app["outgoing_queue"]
    await outgoing_queue.put(None)

    consume_incoming_task = tasks.get("consume_incoming_task")
    if consume_incoming_task:
        await consume_incoming_task

    consume_outgoing_task = tasks.get("consume_outgoing_task")
    if consume_outgoing_task:
        await consume_outgoing_task


def _run_devtools(port: int) -> None:
    app = _make_devtools_aiohttp_app()
    run_app(app, port=port)


def _make_devtools_aiohttp_app(
    size_change_poll_delay_secs: float = DEFAULT_SIZE_CHANGE_POLL_DELAY_SECONDS,
) -> Application:
    app = Application()
    app["size_change_poll_delay_secs"] = size_change_poll_delay_secs
    app["shutdown_event"] = asyncio.Event()
    app["console"] = Console()
    app["incoming_queue"] = Queue()
    app["outgoing_queue"] = Queue()
    app["websockets"] = weakref.WeakSet()
    app["tasks"] = {}
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
