"""Provides classes for holding and managing notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Iterator
from uuid import uuid4

from rich.repr import Result
from typing_extensions import Literal, Self, TypeAlias

SeverityLevel: TypeAlias = Literal["information", "warning", "error"]
"""The severity level for a notification."""


@dataclass
class Notification:
    """Holds the details of a notification."""

    message: str
    """The message for the notification."""

    title: str | None = None
    """The title for the notification."""

    severity: SeverityLevel = "information"
    """The severity level for the notification."""

    timeout: float = 3
    """The timeout for the notification."""

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
        yield "title", self.title, None
        yield "severity", self.severity
        yield "raised_it", self.raised_at
        yield "identity", self.identity
        yield "time_left", self.time_left
        yield "has_expired", self.has_expired


class Notifications:
    """Class for managing a collection of notifications."""

    def __init__(self) -> None:
        """Initialise the notification collection."""
        self._notifications: list[Notification] = []

    def _reap(self) -> Self:
        """Remove any expired notifications from the notification collection."""
        self._notifications = [
            notification
            for notification in self._notifications
            if not notification.has_expired
        ]
        return self

    def add(self, notification: Notification) -> Self:
        """Add the given notification to the collection of managed notifications.

        Args:
            notification: The notification to add.

        Returns:
            Self.
        """
        self._reap()._notifications.append(notification)
        return self

    def __len__(self) -> int:
        """The number of notifications."""
        return len(self._reap()._notifications)

    def __iter__(self) -> Iterator[Notification]:
        return iter(self._reap()._notifications)
