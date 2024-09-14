from __future__ import annotations

from typing import Callable

from textual import events
from textual._callback import invoke
from textual.dom import DOMNode
from textual.errors import DuplicateKeyHandlers
from textual.message_pump import MessagePump


async def dispatch_key(node: DOMNode, event: events.Key) -> bool:
    """Dispatch a key event to method.

    This function will call the method named 'key_<event.key>' on a node if it exists.
    Some keys have aliases. The first alias found will be invoked if it exists.
    If multiple handlers exist that match the key, an exception is raised.

    Args:
        event: A key event.

    Returns:
        True if key was handled, otherwise False.

    Raises:
        DuplicateKeyHandlers: When there's more than 1 handler that could handle this key.
    """

    def get_key_handler(pump: MessagePump, key: str) -> Callable | None:
        """Look for the public and private handler methods by name on self."""
        return getattr(pump, f"key_{key}", None) or getattr(pump, f"_key_{key}", None)

    handled = False
    invoked_method = None
    key_name = event.name
    if not key_name:
        return False

    def _raise_duplicate_key_handlers_error(
        key_name: str, first_handler: str, second_handler: str
    ) -> None:
        """Raise exception for case where user presses a key and there are multiple candidate key handler methods for it."""
        raise DuplicateKeyHandlers(
            f"Multiple handlers for key press {key_name!r}.\n"
            f"We found both {first_handler!r} and {second_handler!r}, "
            f"and didn't know which to call.\n"
            f"Consider combining them into a single handler.",
        )

    try:
        screen = node.screen
    except Exception:
        screen = None
    for key_method_name in event.name_aliases:
        if (key_method := get_key_handler(node, key_method_name)) is not None:
            if invoked_method:
                _raise_duplicate_key_handlers_error(
                    key_name, invoked_method.__name__, key_method.__name__
                )
            # If key handlers return False, then they are not considered handled
            # This allows key handlers to do some conditional logic

            if screen is not None and not screen.is_active:
                break
            handled = (await invoke(key_method, event)) is not False
            invoked_method = key_method

    return handled
