"""
Compatibility layer for asyncio.

"""

from __future__ import annotations

import sys

__all__ = ["create_task"]

if sys.version_info >= (3, 8):
    from asyncio import create_task

else:
    import asyncio
    from asyncio import create_task as _create_task
    from typing import Awaitable

    def create_task(coroutine: Awaitable, *, name: str | None = None) -> asyncio.Task:
        """Schedule the execution of a coroutine object in a spawn task."""
        return _create_task(coroutine)
