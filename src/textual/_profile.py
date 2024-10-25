"""
Timer context manager, only used in debug.
"""

import contextlib
from time import perf_counter
from typing import Generator

from textual import log


@contextlib.contextmanager
def timer(subject: str = "time") -> Generator[None, None, None]:
    """print the elapsed time. (only used in debugging)"""
    start = perf_counter()
    yield
    elapsed = perf_counter() - start
    elapsed_ms = elapsed * 1000
    log(f"{subject} elapsed {elapsed_ms:.4f}ms")
