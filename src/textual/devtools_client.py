from __future__ import annotations

import asyncio
import base64
import datetime
import json
import pickle
from asyncio import Queue, Task, QueueFull
from contextlib import suppress
from io import StringIO
from typing import Type, Any

import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError, ClientWebSocketResponse
from rich.console import Console
from rich.segment import Segment

from textual.devtools import DEFAULT_PORT

WEBSOCKET_CONNECT_TIMEOUT = 3
LOG_QUEUE_MAXSIZE = 512


class DevtoolsConsole(Console):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.record = True

    def export_segments(self) -> list[Segment]:
        with self._record_buffer_lock:
            segments = self._record_buffer[:]
            self._record_buffer.clear()
        return segments


class DetachDevtools:
    pass


class DevtoolsConnectionError(Exception):
    pass


class DevtoolsClient:
    def __init__(self, address: str = "127.0.0.1", port: int = DEFAULT_PORT):
        self.url: str = f"ws://{address}:{port}"
        self.session: aiohttp.ClientSession | None = None
        self.log_queue_task: Task | None = None
        self.update_console_task: Task | None = None
        self.console: DevtoolsConsole = DevtoolsConsole(file=StringIO())
        self.websocket: ClientWebSocketResponse | None = None
        self.log_queue: Queue | None = None
        self.spillover: int = 0

    async def connect(self) -> None:
        self.session = aiohttp.ClientSession()
        self.log_queue: Queue[str | Type[DetachDevtools]] = Queue(
            maxsize=LOG_QUEUE_MAXSIZE
        )
        try:
            self.websocket = await self.session.ws_connect(
                f"{self.url}/textual-devtools-websocket",
                timeout=WEBSOCKET_CONNECT_TIMEOUT,
            )
        except (ClientConnectorError, ClientResponseError):
            raise DevtoolsConnectionError()

        log_queue = self.log_queue
        websocket = self.websocket

        async def update_console():
            async for message in self.websocket:
                if message.type == aiohttp.WSMsgType.TEXT:
                    message_json = json.loads(message.data)
                    if message_json["type"] == "server_info":
                        payload = message_json["payload"]
                        self.console.width = payload["width"]
                        self.console.height = payload["height"]

        async def send_queued_logs():
            while True:
                log = await log_queue.get()
                await websocket.send_str(log)
                log_queue.task_done()

        self.log_queue_task = asyncio.create_task(send_queued_logs())
        self.update_console_task = asyncio.create_task(update_console())

    async def cancel_tasks(self):
        await self.cancel_log_queue_processing()
        await self.cancel_console_size_updates()

    async def cancel_log_queue_processing(self) -> None:
        if self.log_queue_task:
            self.log_queue_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.log_queue_task

    async def cancel_console_size_updates(self) -> None:
        if self.update_console_task:
            self.update_console_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.update_console_task

    async def disconnect(self) -> None:
        """Disconnect from the devtools server by cancelling tasks and closing connections"""
        await self.cancel_tasks()
        await self._close_connections()

    @property
    def is_connected(self):
        if not self.session or not self.websocket:
            return False
        return not (self.session.closed or self.websocket.closed)

    async def _close_connections(self) -> None:
        await self.websocket.close()
        await self.session.close()

    def log(self, *objects: Any, path: str = "", lineno: int = 0) -> None:
        self.console.print(*objects)
        segments = self.console.export_segments()

        encoded_segments = self._encode_segments(segments)
        message = json.dumps(
            {
                "type": "client_log",
                "payload": {
                    "timestamp": int(datetime.datetime.utcnow().timestamp()),
                    "path": path,
                    "line_number": lineno,
                    "encoded_segments": encoded_segments,
                },
            }
        )
        try:
            self.log_queue.put_nowait(message)
            if self.spillover > 0 and self.log_queue.qsize() < LOG_QUEUE_MAXSIZE:
                # Tell the server how many messages we had to discard due
                # to the log queue filling to capacity on the client.
                spillover_message = json.dumps(
                    {
                        "type": "client_spillover",
                        "payload": {
                            "spillover": self.spillover,
                        },
                    }
                )
                self.log_queue.put_nowait(spillover_message)
                self.spillover = 0
        except QueueFull:
            self.spillover += 1

    def _encode_segments(self, segments: list[Segment]) -> str:
        """Pickle and Base64 encode the list of Segments"""
        pickled = pickle.dumps(segments, protocol=3)
        encoded = base64.b64encode(pickled)
        return str(encoded, encoding="utf-8")
