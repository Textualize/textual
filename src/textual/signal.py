from __future__ import annotations

from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

import rich.repr

if TYPE_CHECKING:
    from ._types import CallbackType
    from .dom import DOMNode


@rich.repr.auto(angular=True)
class Signal:
    """A signal that a widget may subscribe to, in order to receive Signal events."""

    def __init__(self, owner: DOMNode) -> None:
        """Initialize a signal.

        Args:
            owner: The owner of this signal.
        """
        self._owner = owner
        self._subscriptions: WeakKeyDictionary[
            DOMNode, list[CallbackType]
        ] = WeakKeyDictionary()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._owner
        yield "subscriptions", list(self._subscriptions.keys())

    def subscribe(self, node: DOMNode, callback: CallbackType) -> None:
        """Subscribe a node to this signal.

        When the signal is published, the node will receive a [Signal][textual.events.Signal] event.

        Args:
            node: Node to subscribe.
        """
        callbacks = self._subscriptions.setdefault(node, [])
        if callback not in callbacks:
            callbacks.append(callback)

    def unsubscribe(self, node: DOMNode) -> None:
        """Unsubscribe a node from this signal.

        Args:
            node: Node to unsubscribe,
        """
        self._subscriptions.pop(node, None)

    def publish(self) -> int:
        """Publish the signal (invoke subscribed callbacks)

        Returns:
            The number of messages sent.
        """
        count = 0
        for node, callbacks in self._subscriptions.items():
            for callback in callbacks:
                node.call_next(callback)
                count += 1

        return count
