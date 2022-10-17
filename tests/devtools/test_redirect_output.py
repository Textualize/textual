from contextlib import redirect_stdout
from datetime import datetime

import msgpack
import time_machine

from textual.devtools.redirect_output import StdoutRedirector

TIMESTAMP = 1649166819


@time_machine.travel(datetime.utcfromtimestamp(TIMESTAMP))
async def test_print_redirect_to_devtools_only(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        print("Hello, world!")

    assert devtools.log_queue.qsize() == 1

    queued_log = await devtools.log_queue.get()
    queued_log_data = msgpack.unpackb(queued_log)
    print(repr(queued_log_data))
    payload = queued_log_data["payload"]

    assert queued_log_data["type"] == "client_log"
    assert payload["timestamp"] == TIMESTAMP
    assert (
        payload["segments"]
        == b"\x80\x04\x95B\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x0crich.segment\x94\x8c\x07Segment\x94\x93\x94\x8c\rHello, world!\x94NN\x87\x94\x81\x94h\x03\x8c\x01\n\x94NN\x87\x94\x81\x94e."
    )


async def test_print_redirect_to_logfile_only(devtools):
    await devtools.disconnect()
    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        print("Hello, world!")


async def test_print_redirect_to_devtools_and_logfile(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        print("Hello, world!")

    assert devtools.log_queue.qsize() == 1


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_without_flush_not_sent_to_devtools(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        # End is no longer newline character, so print will no longer
        # flush the output buffer by default.
        print("Hello, world!", end="")

    assert devtools.log_queue.qsize() == 0


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_forced_flush_sent_to_devtools(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        print("Hello, world!", end="", flush=True)

    assert devtools.log_queue.qsize() == 1


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_multiple_args_batched_as_one_log(devtools):
    await devtools._stop_log_queue_processing()
    redirector = StdoutRedirector(devtools)
    with redirect_stdout(redirector):  # type: ignore
        # This print adds 3 messages to the buffer that can be batched
        print("The first", "batch", "of logs", end="")
        # This message cannot be batched with the previous message,
        # and so it will be the 2nd item added to the log queue.
        print("I'm in the second batch")

    assert devtools.log_queue.qsize() == 2


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_print_strings_containing_newline_flushed(devtools):
    await devtools._stop_log_queue_processing()

    with redirect_stdout(StdoutRedirector(devtools)):  # type: ignore
        # Flushing is disabled since end="", but the first
        # string will be flushed since it contains a newline
        print("Hel\nlo", end="")
        print("world", end="")

    assert devtools.log_queue.qsize() == 1


@time_machine.travel(datetime.fromtimestamp(TIMESTAMP))
async def test_flush_flushes_buffered_logs(devtools):
    await devtools._stop_log_queue_processing()

    redirector = StdoutRedirector(devtools)
    with redirect_stdout(redirector):  # type: ignore
        print("x", end="")

    assert devtools.log_queue.qsize() == 0
    redirector.flush()
    assert devtools.log_queue.qsize() == 1
