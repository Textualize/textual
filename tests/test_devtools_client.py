import json
from asyncio import Queue
from datetime import datetime

import pytest
import time_machine

from textual.devtools import make_aiohttp_app
from textual.devtools_client import DevtoolsClient

TIMESTAMP = 1649166819


@pytest.fixture
async def devtools(aiohttp_client, aiohttp_server, unused_tcp_port):
    server = await aiohttp_server(make_aiohttp_app(), port=unused_tcp_port)
    client = await aiohttp_client(server)
    devtools = DevtoolsClient(address=client.host, port=client.port)
    await devtools.connect()
    yield devtools
    await devtools.disconnect()
    await client.close()
    await server.close()


def test_devtools_client_initialize_defaults():
    devtools = DevtoolsClient()
    assert devtools.url == "ws://127.0.0.1:8081"


async def test_devtools_client_is_connected(devtools):
    assert devtools.is_connected


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_devtools_log_places_encodes_and_queues_message(devtools):
    log = "Hello, world!"
    expected_queued_log =  {
        "payload": {
            "encoded_segments": "gASVQgAAAAAAAABdlCiMDHJpY2guc2VnbWVudJSMB1NlZ"
            "21lbnSUk5SMDUhlbGxvLCB3b3JsZCGUTk6HlIGUaAOMAQqUTk6HlIGUZS4=",
            "line_number": 0,
            "path": "",
            "timestamp": TIMESTAMP,
        },
        "type": "client_log",
    }

    devtools.log(log)
    queued_log = await devtools.log_queue.get()

    queued_log_json = json.loads(queued_log)
    assert queued_log_json == expected_queued_log
