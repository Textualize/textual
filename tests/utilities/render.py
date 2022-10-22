import asyncio
import io
import re
from typing import Callable

import pytest
from rich.console import Console, RenderableType

re_link_ids = re.compile(r"id=[\d\.\-]*?;.*?\x1b")


def replace_link_ids(render: str) -> str:
    """Link IDs have a random ID and system path which is a problem for
    reproducible tests.

    """
    return re_link_ids.sub("id=0;foo\x1b", render)


def render(renderable: RenderableType, no_wrap: bool = False) -> str:
    console = Console(
        width=100, file=io.StringIO(), color_system="truecolor", legacy_windows=False
    )
    with console.capture() as capture:
        console.print(renderable, no_wrap=no_wrap, end="")
    output = replace_link_ids(capture.get())
    return output


async def wait_for_predicate(
    predicate: Callable[[], bool],
    timeout_secs: float = 2,
    poll_delay_secs: float = 0.001,
) -> None:
    """Wait for the given predicate to become True by evaluating it every `poll_delay_secs`
    seconds. Fail the pytest test if the predicate does not become True after `timeout_secs`
    seconds.

    Args:
        predicate (Callable[[], bool]): The predicate function which will be called repeatedly.
        timeout_secs (float): If the predicate doesn't evaluate to True after this number of
            seconds, the test will fail.
        poll_delay_secs (float): The number of seconds to wait between each call to the
            predicate function.
    """
    time_taken = 0
    while True:
        result = predicate()
        if result:
            return
        await asyncio.sleep(poll_delay_secs)
        time_taken += poll_delay_secs
        if time_taken > timeout_secs:
            pytest.fail(
                f"Predicate {predicate} did not return True after {timeout_secs} seconds."
            )
