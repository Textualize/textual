from __future__ import annotations

from typing import Any, NamedTuple


class NoHandler(Exception):
    pass


class HandlerArguments(NamedTuple):
    modifiers: set[str]
    action: str


def extract_handler_actions(event_name: str, meta: dict[str, Any]) -> HandlerArguments:
    event_path = event_name.split(".")
    for key, value in meta.items():
        if key.startswith("@"):
            name_args = key[1:].split(".")
            if name_args[: len(event_path)] == event_path:
                modifiers = name_args[len(event_path) :]
                return HandlerArguments(set(modifiers), value)
    raise NoHandler(f"No handler for {event_name!r}")


if __name__ == "__main__":

    print(extract_handler_actions("mouse.down", {"@mouse.down.hot": "app.bell()"}))
