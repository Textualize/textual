import json
import types
from asyncio import Queue
from datetime import datetime

import msgpack
import time_machine
from aiohttp.web_ws import WebSocketResponse
from rich.console import ConsoleDimensions
from rich.panel import Panel

from tests.utilities.render import wait_for_predicate
from textual.devtools.client import DevtoolsClient
from textual.devtools.redirect_output import DevtoolsLog

CALLER_LINENO = 123
CALLER_PATH = "a/b/c.py"
CALLER = types.SimpleNamespace(filename=CALLER_PATH, lineno=CALLER_LINENO)
TIMESTAMP = 1649166819


def test_devtools_client_initialize_defaults():
    devtools = DevtoolsClient()
    assert devtools.url == "ws://127.0.0.1:8081"


async def test_devtools_client_is_connected(devtools):
    assert devtools.is_connected


@time_machine.travel(datetime.utcfromtimestamp(TIMESTAMP))
async def test_devtools_log_places_encodes_and_queues_message(devtools):
    await devtools._stop_log_queue_processing()
    devtools.log(DevtoolsLog("Hello, world!", CALLER))
    queued_log = await devtools.log_queue.get()
    queued_log_data = msgpack.unpackb(queued_log)
    print(repr(queued_log_data))


@time_machine.travel(datetime.utcfromtimestamp(TIMESTAMP))
async def test_devtools_log_places_encodes_and_queues_many_logs_as_string(devtools):
    await devtools._stop_log_queue_processing()
    devtools.log(DevtoolsLog(("hello", "world"), CALLER))
    queued_log = await devtools.log_queue.get()
    queued_log_data = msgpack.unpackb(queued_log)
    print(repr(queued_log_data))
    assert queued_log_data == {
        "type": "client_log",
        "payload": {
            "group": 0,
            "verbosity": 0,
            "timestamp": 1649166819,
            "path": "a/b/c.py",
            "line_number": 123,
            "segments": b"\x80\x04\x95@\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x0crich.segment\x94\x8c\x07Segment\x94\x93\x94\x8c\x0bhello world\x94NN\x87\x94\x81\x94h\x03\x8c\x01\n\x94NN\x87\x94\x81\x94e.",
        },
    }


async def test_devtools_log_spillover(devtools):
    # Give the devtools an intentionally small max queue size
    await devtools._stop_log_queue_processing()
    devtools.log_queue = Queue(maxsize=2)

    # Force spillover of 2
    devtools.log(DevtoolsLog((Panel("hello, world"),), CALLER))
    devtools.log(DevtoolsLog("second message", CALLER))
    devtools.log(DevtoolsLog("third message", CALLER))  # Discarded by rate-limiting
    devtools.log(DevtoolsLog("fourth message", CALLER))  # Discarded by rate-limiting

    assert devtools.spillover == 2

    # Consume log queue
    while not devtools.log_queue.empty():
        await devtools.log_queue.get()

    # Add another message now that we're under spillover threshold
    devtools.log(DevtoolsLog("another message", CALLER))
    await devtools.log_queue.get()

    # Ensure we're informing the server of spillover rate-limiting
    spillover_message = await devtools.log_queue.get()
    assert json.loads(spillover_message) == {
        "type": "client_spillover",
        "payload": {"spillover": 2},
    }


async def test_devtools_client_update_console_dimensions(devtools, server):
    """Sending new server info through websocket from server to client should (eventually)
    result in the dimensions of the devtools client console being updated to match.
    """
    server_to_client: WebSocketResponse = next(
        iter(server.app["service"].clients)
    ).websocket
    server_info = {
        "type": "server_info",
        "payload": {
            "width": 123,
            "height": 456,
        },
    }
    await server_to_client.send_json(server_info)
    await wait_for_predicate(
        lambda: devtools.console.size == ConsoleDimensions(123, 456)
    )
