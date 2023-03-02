from __future__ import annotations

import asyncio
import inspect
import json
import pickle
from asyncio import Queue, QueueFull, Task
from io import StringIO
from time import time
from typing import Any, NamedTuple, Type

import aiohttp
import msgpack
from aiohttp import ClientConnectorError, ClientResponseError, ClientWebSocketResponse
from rich.console import Console
from rich.segment import Segment

from .._log import LogGroup, LogVerbosity

DEVTOOLS_PORT = 8081
WEBSOCKET_CONNECT_TIMEOUT = 3
LOG_QUEUE_MAXSIZE = 512


class DevtoolsLog(NamedTuple):
    """A devtools log message.

    Attributes:
        objects_or_string: Corresponds to the data that will
            ultimately be passed to Console.print in order to generate the log
            Segments.
        caller: Information about where this log message was
            created. In other words, where did the user call `print` or `App.log`
            from. Used to display line number and file name in the devtools window.
    """

    objects_or_string: tuple[Any, ...] | str
    caller: inspect.Traceback


class DevtoolsConsole(Console):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.record = True

    def export_segments(self) -> list[Segment]:
        """Return the list of Segments that have be printed using this console

        Returns:
            The list of Segments that have been printed using this console
        """
        with self._record_buffer_lock:
            segments = self._record_buffer[:]
            self._record_buffer.clear()
        return segments


class DevtoolsConnectionError(Exception):
    """Raise when the devtools client is unable to connect to the server"""


class ClientShutdown:
    """Sentinel type sent to client queue(s) to indicate shutdown"""


class DevtoolsClient:
    """Client responsible for websocket communication with the devtools server.
    Communicates using a simple JSON protocol.

    Messages have the format `{"type": <str>, "payload": <json>}`.

    Valid values for `"type"` (that can be sent from client -> server) are
    `"client_log"` (for log messages) and `"client_spillover"` (for reporting
    to the server that messages were discarded due to rate limiting).

    A `"client_log"` message has a `"payload"` format as follows:
    ```
    {"timestamp": <int, unix timestamp>,
     "path": <str, path of file>,
     "line_number": <int, line number log was made from>,
     "encoded_segments": <str, pickled then b64 encoded Segments to log>}
    ```

    A `"client_spillover"` message has a `"payload"` format as follows:
    ```
    {"spillover": <int, the number of messages discarded by rate-limiting>}
    ```

    Args:
        host: The host the devtools server is running on, defaults to "127.0.0.1"
        port: The port the devtools server is accessed via, defaults to 8081
    """

    def __init__(self, host: str = "127.0.0.1", port: int = DEVTOOLS_PORT) -> None:
        self.url: str = f"ws://{host}:{port}"
        self.session: aiohttp.ClientSession | None = None
        self.log_queue_task: Task | None = None
        self.update_console_task: Task | None = None
        self.console: DevtoolsConsole = DevtoolsConsole(file=StringIO())
        self.websocket: ClientWebSocketResponse | None = None
        self.log_queue: Queue[str | bytes | Type[ClientShutdown]] | None = None
        self.spillover: int = 0
        self.verbose: bool = False

    async def connect(self) -> None:
        """Connect to the devtools server.

        Raises:
            DevtoolsConnectionError: If we're unable to establish
                a connection to the server for any reason.
        """
        self.session = aiohttp.ClientSession()
        self.log_queue = Queue(maxsize=LOG_QUEUE_MAXSIZE)
        try:
            self.websocket = await self.session.ws_connect(
                f"{self.url}/textual-devtools-websocket",
                timeout=WEBSOCKET_CONNECT_TIMEOUT,
            )
        except (ClientConnectorError, ClientResponseError):
            raise DevtoolsConnectionError()

        log_queue = self.log_queue
        websocket = self.websocket

        async def update_console() -> None:
            """Coroutine function scheduled as a Task, which listens on
            the websocket for updates from the server regarding any changes
            in the server Console dimensions. When the client learns of this
            change, it will update its own Console to ensure it renders at
            the correct width for server-side display.
            """
            assert self.websocket is not None
            async for message in self.websocket:
                if message.type == aiohttp.WSMsgType.TEXT:
                    message_json = json.loads(message.data)
                    if message_json["type"] == "server_info":
                        payload = message_json["payload"]
                        self.console.width = payload["width"]
                        self.console.height = payload["height"]
                        self.verbose = payload.get("verbose", False)

        async def send_queued_logs():
            """Coroutine function which is scheduled as a Task, which consumes
            messages from the log queue and sends them to the server via websocket.
            """
            while True:
                log = await log_queue.get()
                if log is ClientShutdown:
                    log_queue.task_done()
                    break
                if isinstance(log, str):
                    await websocket.send_str(log)
                else:
                    assert isinstance(log, bytes)
                    await websocket.send_bytes(log)
                log_queue.task_done()

        self.log_queue_task = asyncio.create_task(send_queued_logs())
        self.update_console_task = asyncio.create_task(update_console())

    async def _stop_log_queue_processing(self) -> None:
        """Schedule end of processing of the log queue, meaning that any messages a
        user logs will be added to the queue, but not consumed and sent to
        the server.
        """
        if self.log_queue is not None:
            await self.log_queue.put(ClientShutdown)
        if self.log_queue_task:
            await self.log_queue_task

    async def _stop_incoming_message_processing(self) -> None:
        """Schedule stop of the task which listens for incoming messages from the
        server around changes in the server console size.
        """
        if self.websocket:
            await self.websocket.close()
        if self.update_console_task:
            await self.update_console_task
        if self.session:
            await self.session.close()

    async def disconnect(self) -> None:
        """Disconnect from the devtools server by stopping tasks and
        closing connections.
        """
        await self._stop_log_queue_processing()
        await self._stop_incoming_message_processing()

    @property
    def is_connected(self) -> bool:
        """Checks connection to devtools server.

        Returns:
            True if this host is connected to the server. False otherwise.
        """
        if not self.session or not self.websocket:
            return False
        return not (self.session.closed or self.websocket.closed)

    def log(
        self,
        log: DevtoolsLog,
        group: LogGroup = LogGroup.UNDEFINED,
        verbosity: LogVerbosity = LogVerbosity.NORMAL,
    ) -> None:
        """Queue a log to be sent to the devtools server for display.

        Args:
            log: The log to write to devtools
        """
        if isinstance(log.objects_or_string, str):
            self.console.print(log.objects_or_string)
        else:
            self.console.print(*log.objects_or_string)

        segments = self.console.export_segments()

        encoded_segments = self._encode_segments(segments)
        message: bytes | None = msgpack.packb(
            {
                "type": "client_log",
                "payload": {
                    "group": group.value,
                    "verbosity": verbosity.value,
                    "timestamp": int(time()),
                    "path": getattr(log.caller, "filename", ""),
                    "line_number": getattr(log.caller, "lineno", 0),
                    "segments": encoded_segments,
                },
            }
        )
        assert message is not None
        try:
            if self.log_queue:
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

    @classmethod
    def _encode_segments(cls, segments: list[Segment]) -> bytes:
        """Pickle a list of Segments

        Args:
            segments: A list of Segments to encode

        Returns:
            The Segment list pickled with the latest protocol.
        """
        pickled = pickle.dumps(segments, protocol=4)
        return pickled
