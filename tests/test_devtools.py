from datetime import datetime, timezone

import pytest
import time_machine
from rich.align import Align
from rich.console import Console
from rich.segment import Segment

from tests.utilities.render import wait_for_predicate
from textual.devtools.renderables import DevtoolsLogMessage, DevtoolsInternalMessage

TIMESTAMP = 1649166819
WIDTH = 40
# The string "Hello, world!" is encoded in the payload below
EXAMPLE_LOG = {
    "type": "client_log",
    "payload": {
        "encoded_segments": "gASVQgAAAAAAAABdlCiMDHJpY2guc2VnbWVudJSMB1NlZ"
        "21lbnSUk5SMDUhlbGxvLCB3b3JsZCGUTk6HlIGUaAOMAQqUTk6HlIGUZS4=",
        "line_number": 123,
        "path": "abc/hello.py",
        "timestamp": TIMESTAMP,
    },
}


@pytest.fixture(scope="module")
def console():
    return Console(width=WIDTH)


@time_machine.travel(TIMESTAMP)
def test_log_message_render(console):
    message = DevtoolsLogMessage(
        [Segment("content")],
        path="abc/hello.py",
        line_number=123,
        unix_timestamp=TIMESTAMP,
    )
    table = next(iter(message.__rich_console__(console, console.options)))

    assert len(table.rows) == 1

    columns = list(table.columns)
    left_cells = list(columns[0].cells)
    left = left_cells[0]
    right_cells = list(columns[1].cells)
    right: Align = right_cells[0]

    # Since we can't guarantee the timezone the tests will run in...
    local_time = (
        datetime.fromtimestamp(TIMESTAMP)
        .replace(tzinfo=timezone.utc)
        .astimezone(tz=datetime.now().astimezone().tzinfo)
    )
    timezone_name = local_time.tzname()
    string_timestamp = local_time.time()

    assert left == f" [#888177]{string_timestamp} [dim]{timezone_name}[/]"
    assert right.align == "right"
    assert "hello.py:123" in right.renderable


def test_internal_message_render(console):
    message = DevtoolsInternalMessage("hello")
    rule = next(iter(message.__rich_console__(console, console.options)))
    assert rule.title == "hello"
    assert rule.characters == "─"


async def test_devtools_valid_client_log(devtools):
    await devtools.websocket.send_json(EXAMPLE_LOG)
    assert devtools.is_connected


async def test_devtools_string_not_json_message(devtools):
    await devtools.websocket.send_str("ABCDEFG")
    assert devtools.is_connected


async def test_devtools_invalid_json_message(devtools):
    await devtools.websocket.send_json({"invalid": "json"})
    assert devtools.is_connected


async def test_devtools_spillover_message(devtools):
    await devtools.websocket.send_json(
        {"type": "client_spillover", "payload": {"spillover": 123}}
    )
    assert devtools.is_connected


async def test_devtools_console_size_change(server, devtools):
    # Update the width of the console on the server-side
    server.app["console"].width = 124
    # Wait for the client side to update the console on their end
    await wait_for_predicate(lambda: devtools.console.width == 124)
