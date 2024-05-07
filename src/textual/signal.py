"""
Signals are a simple pub-sub mechanism.

DOMNodes can subscribe to a signal, which will invoke a callback when the signal is published.

This is experimental for now, for internal use. It may be part of the public API in a future release.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar, Union
from weakref import WeakKeyDictionary

import rich.repr

from textual import log

if TYPE_CHECKING:
    from .message_pump import MessagePump

SignalT = TypeVar("SignalT")

SignalCallbackType = Union[
    Callable[[SignalT], Awaitable[Any]], Callable[[SignalT], Any]
]


class SignalError(Exception):
    """Raised for Signal errors."""


@rich.repr.auto(angular=True)
class Signal(Generic[SignalT]):
    """A signal that a widget may subscribe to, in order to invoke callbacks when an associated event occurs."""

    def __init__(self, owner: MessagePump, name: str) -> None:
        """Initialize a signal.

        Args:
            owner: The owner of this signal.
            name: An identifier for debugging purposes.
        """
        self._owner = owner
        self._name = name
        self._subscriptions: WeakKeyDictionary[
            MessagePump, list[SignalCallbackType]
        ] = WeakKeyDictionary()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "owner", self._owner
        yield "name", self._name
        yield "subscriptions", list(self._subscriptions.keys())

    def subscribe(self, node: MessagePump, callback: SignalCallbackType) -> None:
        """Subscribe a node to this signal.

        When the signal is published, the callback will be invoked.

        Args:
            node: Node to subscribe.
            callback: A callback function which takes a single argument and returns anything (return type ignored).

        Raises:
            SignalError: Raised when subscribing a non-mounted widget.
        """
        if not node.is_running:
            raise SignalError(
                f"Node must be running to subscribe to a signal (has {node} been mounted)?"
            )
        callbacks = self._subscriptions.setdefault(node, [])
        if callback not in callbacks:
            callbacks.append(callback)

    def unsubscribe(self, node: MessagePump) -> None:
        """Unsubscribe a node from this signal.

        Args:
            node: Node to unsubscribe,
        """
        self._subscriptions.pop(node, None)

    def publish(self, data: SignalT) -> None:
        """Publish the signal (invoke subscribed callbacks).

        Args:
            data: An argument to pass to the callbacks.

        """

        for node, callbacks in list(self._subscriptions.items()):
            if not node.is_running:
                # Removed nodes that are no longer running
                self._subscriptions.pop(node)
            else:
                # Call callbacks
                for callback in callbacks:
                    try:
                        callback(data)
                    except Exception as error:
                        log.error(
                            f"error publishing signal to {node} ignored (callback={callback}); {error}"
                        )
