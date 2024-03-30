"""Provides classes for holding and managing notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Iterator
from uuid import uuid4

from rich.repr import Result
from typing_extensions import Literal, Self, TypeAlias

from .message import Message

SeverityLevel: TypeAlias = Literal["information", "warning", "error"]
"""The severity level for a notification."""


@dataclass
class Notify(Message, bubble=False):
    """Message to show a notification."""

    notification: Notification


@dataclass
class Notification:
    """Holds the details of a notification."""

    message: str
    """The message for the notification."""

    title: str = ""
    """The title for the notification."""

    severity: SeverityLevel = "information"
    """The severity level for the notification."""

    timeout: float = 5
    """The timeout (in seconds) for the notification."""

    raised_at: float = field(default_factory=time)
    """The time when the notification was raised (in Unix time)."""

    identity: str = field(default_factory=lambda: str(uuid4()))
    """The unique identity of the notification."""

    @property
    def time_left(self) -> float:
        """The time left until this notification expires"""
        return (self.raised_at + self.timeout) - time()

    @property
    def has_expired(self) -> bool:
        """Has the notification expired?"""
        return self.time_left <= 0

    def __rich_repr__(self) -> Result:
        yield "message", self.message
        yield "title", self.title, ""
        yield "severity", self.severity
        yield "raised_it", self.raised_at
        yield "identity", self.identity
        yield "time_left", self.time_left
        yield "has_expired", self.has_expired


class Notifications:
    """Class for managing a collection of notifications."""

    def __init__(self) -> None:
        """Initialise the notification collection."""
        self._notifications: dict[str, Notification] = {}

    def _reap(self) -> Self:
        """Remove any expired notifications from the notification collection."""
        for notification in list(self._notifications.values()):
            if notification.has_expired:
                del self._notifications[notification.identity]
        return self

    def add(self, notification: Notification) -> Self:
        """Add the given notification to the collection of managed notifications.

        Args:
            notification: The notification to add.

        Returns:
            Self.
        """
        self._reap()._notifications[notification.identity] = notification
        return self

    def clear(self) -> Self:
        """Clear all the notifications."""
        self._notifications.clear()
        return self

    def __len__(self) -> int:
        """The number of notifications."""
        return len(self._reap()._notifications)

    def __iter__(self) -> Iterator[Notification]:
        return iter(self._reap()._notifications.values())

    def __contains__(self, notification: Notification) -> bool:
        return notification.identity in self._notifications

    def __delitem__(self, notification: Notification) -> None:
        try:
            del self._reap()._notifications[notification.identity]
        except KeyError:
            # An attempt to remove a notification we don't know about is a
            # no-op. What matters here is that the notification is forgotten
            # about, and it looks like a caller has tried to be
            # belt-and-braces. We're fine with this.
            pass
