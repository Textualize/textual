"""
Signals are a simple pub-sub mechanism.

DOMNodes can subscribe to a signal, which will invoke a callback when the signal is published.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar, Union
from weakref import WeakKeyDictionary, ref

import rich.repr

from textual import log

if TYPE_CHECKING:
    from textual.dom import DOMNode

SignalT = TypeVar("SignalT")

SignalCallbackType = Union[
    Callable[[SignalT], Awaitable[Any]], Callable[[SignalT], Any]
]


class SignalError(Exception):
    """Raised for Signal errors."""


@rich.repr.auto(angular=True)
class Signal(Generic[SignalT]):
    """A signal that a widget may subscribe to, in order to invoke callbacks when an associated event occurs."""

    def __init__(self, owner: DOMNode, name: str) -> None:
        """Initialize a signal.

        Args:
            owner: The owner of this signal.
            name: An identifier for debugging purposes.
        """
        self._owner = ref(owner)
        self._name = name
        self._subscriptions: WeakKeyDictionary[
            DOMNode, list[SignalCallbackType[SignalT]]
        ] = WeakKeyDictionary()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "owner", self.owner
        yield "name", self._name
        yield "subscriptions", list(self._subscriptions.keys())

    @property
    def owner(self) -> DOMNode | None:
        """The owner of this Signal, or `None` if there is no owner."""
        return self._owner()

    def subscribe(
        self,
        node: DOMNode,
        callback: SignalCallbackType[SignalT],
        immediate: bool = False,
    ) -> None:
        """Subscribe a node to this signal.

        When the signal is published, the callback will be invoked.

        Args:
            node: Node to subscribe.
            callback: A callback function which takes a single argument and returns anything (return type ignored).
            immediate: Invoke the callback immediately on publish if `True`, otherwise post it to the DOM node to be
                called once existing messages have been processed.

        Raises:
            SignalError: Raised when subscribing a non-mounted widget.
        """

        if not node.is_running:
            raise SignalError(
                f"Node must be running to subscribe to a signal (has {node} been mounted)?"
            )

        if immediate:

            def signal_callback(data: SignalT) -> None:
                """Invoke the callback immediately."""
                callback(data)

        else:

            def signal_callback(data: SignalT) -> None:
                """Post the callback to the node, to call at the next opertunity."""
                node.call_next(callback, data)

        callbacks = self._subscriptions.setdefault(node, [])
        callbacks.append(signal_callback)

    def unsubscribe(self, node: DOMNode) -> None:
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
        # Don't publish if the DOM is not ready or shutting down
        owner = self.owner
        if owner is None:
            return
        if not owner.is_attached or owner._pruning:
            return
        for ancestor_node in owner.ancestors_with_self:
            if not ancestor_node.is_running:
                return

        for node, callbacks in list(self._subscriptions.items()):
            if not (node.is_running and node.is_attached) or node._pruning:
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
