import json
import pprint
from contextlib import redirect_stdout
from datetime import datetime

import time_machine

from textual.devtools.redirect_output import DevtoolsRedirector

TIMESTAMP = 1649166819


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_is_redirected_to_devtools(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(DevtoolsRedirector(devtools)):
        print("Hello, world!")

    assert devtools.log_queue.qsize() == 1

    queued_log = await devtools.log_queue.get()
    queued_log_json = json.loads(queued_log)
    payload = queued_log_json["payload"]

    assert queued_log_json["type"] == "client_log"
    assert payload["timestamp"] == TIMESTAMP
    assert (
            payload["encoded_segments"]
            == "gANdcQAoY3JpY2guc2VnbWVudApTZWdtZW50CnEBWA0AAABIZWxsbywgd29ybGQhcQJOTodxA4FxBGgBWAEAAAAKcQVOTodxBoFxB2Uu"
    )


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_without_flush_not_sent_to_devtools(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(DevtoolsRedirector(devtools)):
        # End is no longer newline character, so print will no longer
        # flush the output buffer by default.
        print("Hello, world!", end="")

    assert devtools.log_queue.qsize() == 0


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_forced_flush_sent_to_devtools(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(DevtoolsRedirector(devtools)):
        print("Hello, world!", end="", flush=True)

    assert devtools.log_queue.qsize() == 1


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_multiple_args_batched_as_one_log(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(DevtoolsRedirector(devtools)):
        # We call print with multiple arguments here, but it
        # results in a single log added to the log queue.
        print("Hello", "world", "multiple")

    assert devtools.log_queue.qsize() == 1

    queued_log = await devtools.log_queue.get()
    queued_log_json = json.loads(queued_log)
    payload = queued_log_json["payload"]

    assert queued_log_json["type"] == "client_log"
    assert payload["timestamp"] == TIMESTAMP
    assert payload[
               "encoded_segments"] == "gANdcQAoY3JpY2guc2VnbWVudApTZWdtZW50CnEBWBQAAABIZWxsbyB3b3JsZCBtdWx0aXBsZXECTk6HcQOBcQRoAVgBAAAACnEFTk6HcQaBcQdlLg=="
    assert len(payload["path"]) > 0
    assert payload["line_number"] != 0


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_multiple_args_batched_as_one_log(devtools):
    await devtools._stop_log_queue_processing()
    redirector = DevtoolsRedirector(devtools)
    with redirect_stdout(redirector):
        # This print adds 3 messages to the buffer that can be batched
        print("The first", "batch", "of logs", end="")
        # This message cannot be batched with the previous message,
        # and so it will be the 2nd item added to the log queue.
        print("I'm in the second batch")

    assert devtools.log_queue.qsize() == 2


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_strings_containing_newline_flushed(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(DevtoolsRedirector(devtools)):
        # Flushing is disabled since end="", but the first
        # string will be flushed since it contains a newline
        print("Hel\nlo", end="")
        print("world", end="")

    assert devtools.log_queue.qsize() == 1


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_flush_flushes_buffered_logs(devtools):
    await devtools._stop_log_queue_processing()

    redirector = DevtoolsRedirector(devtools)
    with redirect_stdout(redirector):
        print("x", end="")

    assert devtools.log_queue.qsize() == 0
    redirector.flush()
    assert devtools.log_queue.qsize() == 1
