from __future__ import annotations

from typing import Any, NamedTuple


class NoHandler(Exception):
    """Raised when handler isn't found in the meta."""


class HandlerArguments(NamedTuple):
    """Information for event handler."""

    modifiers: set[str]
    action: Any


def extract_handler_actions(event_name: str, meta: dict[str, Any]) -> HandlerArguments:
    """Extract action from meta dict.

    Args:
        event_name: Event to check from.
        meta: Meta information (stored in Rich Style)

    Raises:
        NoHandler: If no handler is found.

    Returns:
        Action information.
    """
    event_path = event_name.split(".")
    for key, value in meta.items():
        if key.startswith("@"):
            name_args = key[1:].split(".")
            if name_args[: len(event_path)] == event_path:
                modifiers = name_args[len(event_path) :]
                return HandlerArguments(set(modifiers), value)
    raise NoHandler(f"No handler for {event_name!r}")
