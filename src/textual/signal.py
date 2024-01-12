from __future__ import annotations

from copy import copy
from weakref import WeakKeyDictionary

import rich.repr

from . import events
from .dom import DOMNode


@rich.repr.auto(angular=True)
class Signal:
    """A signal that a widget may subscribe to, in order to receive Signal events."""

    def __init__(self) -> None:
        self._subscriptions: WeakKeyDictionary[DOMNode, None] = WeakKeyDictionary()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "subscriptions", list(self._subscriptions.keys())

    def subscribe(self, node: DOMNode) -> None:
        """Subscribe a node to this signal.

        When the signal is published, the node will receive a [Signal][textual.events.Signal] event.

        Args:
            node: Node to subscribe.
        """
        if node not in self._subscriptions:
            self._subscriptions[node] = None

    def publish(self, message: events.Signal) -> int:
        """Publish a message.

        Args:
            message: Signal event to send.

        Returns:
            The number of messages sent.
        """
        count = 0
        for node in self._subscriptions.keys():
            node.post_message(copy(message))
            count += 1
        return count
