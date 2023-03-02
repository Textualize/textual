"""Manages a running devtools instance"""
from __future__ import annotations

import asyncio
import json
import pickle
from json import JSONDecodeError
from typing import Any

import msgpack
from aiohttp import WSMsgType
from aiohttp.abc import Request
from aiohttp.web_ws import WebSocketResponse
from rich.console import Console
from rich.markup import escape

from textual._log import LogGroup
from textual._time import time
from textual.devtools.renderables import (
    DevConsoleHeader,
    DevConsoleLog,
    DevConsoleNotice,
)

QUEUEABLE_TYPES = {"client_log", "client_spillover"}


class DevtoolsService:
    """A running instance of devtools has a single DevtoolsService which is
    responsible for tracking connected client applications.
    """

    def __init__(
        self,
        update_frequency: float,
        verbose: bool = False,
        exclude: list[str] | None = None,
    ) -> None:
        """
        Args:
            update_frequency: The number of seconds to wait between
                sending updates of the console size to connected clients.
            verbose: Enable verbose logging on client.
            exclude: List of log groups to exclude from output.
        """
        self.update_frequency = update_frequency
        self.verbose = verbose
        self.exclude = set(name.upper() for name in exclude) if exclude else set()
        self.console = Console()
        self.shutdown_event = asyncio.Event()
        self.clients: list[ClientHandler] = []

    async def start(self):
        """Starts devtools tasks"""
        self.size_poll_task = asyncio.create_task(self._console_size_poller())
        self.console.print(DevConsoleHeader(verbose=self.verbose))

    @property
    def clients_connected(self) -> bool:
        """Returns True if there are connected clients, False otherwise."""
        return len(self.clients) > 0

    async def _console_size_poller(self) -> None:
        """Poll console dimensions, and add a `server_info` message to the Queue
        any time a change occurs. We only poll if there are clients connected,
        and if we're not shutting down the server.
        """
        current_width = self.console.width
        current_height = self.console.height
        await self._send_server_info_to_all()
        while not self.shutdown_event.is_set():
            width = self.console.width
            height = self.console.height
            dimensions_changed = width != current_width or height != current_height
            if dimensions_changed:
                await self._send_server_info_to_all()
                current_width = width
                current_height = height
            try:
                await asyncio.wait_for(
                    self.shutdown_event.wait(), timeout=self.update_frequency
                )
            except asyncio.TimeoutError:
                pass

    async def _send_server_info_to_all(self) -> None:
        """Add `server_info` message to the queues of every client"""
        for client_handler in self.clients:
            await self.send_server_info(client_handler)

    async def send_server_info(self, client_handler: ClientHandler) -> None:
        """Send information about the server e.g. width and height of Console to
        a connected client.

        Args:
            client_handler: The client to send information to
        """
        await client_handler.send_message(
            {
                "type": "server_info",
                "payload": {
                    "width": self.console.width,
                    "height": self.console.height,
                    "verbose": self.verbose,
                },
            }
        )

    async def handle(self, request: Request) -> WebSocketResponse:
        """Handles a single client connection"""
        client = ClientHandler(request, service=self)
        self.clients.append(client)
        websocket = await client.run()
        self.clients.remove(client)
        return websocket

    async def shutdown(self) -> None:
        """Stop server async tasks and clean up all client handlers"""

        # Stop polling/writing Console dimensions to clients
        self.shutdown_event.set()
        await self.size_poll_task

        # We're shutting down the server, so inform all connected clients
        for client in self.clients:
            await client.close()
        self.clients.clear()


class ClientHandler:
    """Handles a single client connection to the devtools.
    A single DevtoolsService managers many ClientHandlers. A single ClientHandler
    corresponds to a single running Textual application instance, and is responsible
    for communication with that Textual app.
    """

    def __init__(self, request: Request, service: DevtoolsService) -> None:
        """
        Args:
            request: The aiohttp.Request associated with this client
            service: The parent DevtoolsService which is responsible
                for the handling of this client.
        """
        self.request = request
        self.service = service
        self.websocket = WebSocketResponse()

    async def send_message(self, message: dict[str, object]) -> None:
        """Send a message to a client

        Args:
            message: The dict which will be sent
                to the client.
        """
        await self.outgoing_queue.put(message)

    async def _consume_outgoing(self) -> None:
        """Consume messages from the outgoing (server -> client) Queue."""
        while True:
            message_json = await self.outgoing_queue.get()
            if message_json is None:
                self.outgoing_queue.task_done()
                break
            type = message_json["type"]
            if type == "server_info":
                await self.websocket.send_json(message_json)
            self.outgoing_queue.task_done()

    async def _consume_incoming(self) -> None:
        """Consume messages from the incoming (client -> server) Queue, and print
        the corresponding renderables to the console for each message.
        """
        last_message_time: float | None = None
        while True:
            message = await self.incoming_queue.get()
            if message is None:
                self.incoming_queue.task_done()
                break

            type = message["type"]
            if type == "client_log":
                payload = message["payload"]
                if LogGroup(payload.get("group", 0)).name in self.service.exclude:
                    continue
                encoded_segments = payload["segments"]
                segments = pickle.loads(encoded_segments)
                message_time = time()
                if (
                    last_message_time is not None
                    and message_time - last_message_time > 0.5
                ):
                    # Print a rule if it has been longer than half a second since the last message
                    self.service.console.rule()
                self.service.console.print(
                    DevConsoleLog(
                        segments=segments,
                        path=payload["path"],
                        line_number=payload["line_number"],
                        unix_timestamp=payload["timestamp"],
                        group=payload.get("group", 0),
                        verbosity=payload.get("verbosity", 0),
                        severity=payload.get("severity", 0),
                    )
                )
                last_message_time = message_time
            elif type == "client_spillover":
                spillover = int(message["payload"]["spillover"])
                info_renderable = DevConsoleNotice(
                    f"Discarded {spillover} messages", level="warning"
                )
                self.service.console.print(info_renderable)
            self.incoming_queue.task_done()

    async def run(self) -> WebSocketResponse:
        """Prepare the websocket and communication queues, and continuously
        read messages from the queues.

        Returns:
            The WebSocketResponse associated with this client.
        """

        await self.websocket.prepare(self.request)
        self.incoming_queue: asyncio.Queue[dict | None] = asyncio.Queue()
        self.outgoing_queue: asyncio.Queue[dict | None] = asyncio.Queue()
        self.outgoing_messages_task = asyncio.create_task(self._consume_outgoing())
        self.incoming_messages_task = asyncio.create_task(self._consume_incoming())

        if self.request.remote:
            self.service.console.print(
                DevConsoleNotice(f"Client '{escape(self.request.remote)}' connected")
            )
        try:
            await self.service.send_server_info(client_handler=self)
            async for websocket_message in self.websocket:
                if websocket_message.type in (WSMsgType.TEXT, WSMsgType.BINARY):
                    message: dict[str, Any]
                    try:
                        if isinstance(websocket_message.data, bytes):
                            message = msgpack.unpackb(websocket_message.data)
                        else:
                            message = json.loads(websocket_message.data)
                    except JSONDecodeError:
                        self.service.console.print(escape(str(websocket_message.data)))
                        continue

                    type = message.get("type")
                    if not type:
                        continue
                    if (
                        type in QUEUEABLE_TYPES
                        and not self.service.shutdown_event.is_set()
                    ):
                        await self.incoming_queue.put(message)
                elif websocket_message.type == WSMsgType.ERROR:
                    self.service.console.print(
                        DevConsoleNotice("Websocket error occurred", level="error")
                    )
                    break
        except Exception as error:
            self.service.console.print(DevConsoleNotice(str(error), level="error"))
        finally:
            if self.request.remote:
                self.service.console.print(
                    "\n",
                    DevConsoleNotice(
                        f"Client '{escape(self.request.remote)}' disconnected"
                    ),
                )
            await self.close()

        return self.websocket

    async def close(self) -> None:
        """Stop all incoming/outgoing message processing,
        and shutdown the websocket connection associated with this
        client.
        """

        # Stop any writes to the websocket first
        await self.outgoing_queue.put(None)
        await self.outgoing_messages_task

        # Now we can shut the socket down
        await self.websocket.close()

        # This task is independent of the websocket
        await self.incoming_queue.put(None)
        await self.incoming_messages_task
