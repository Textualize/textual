from __future__ import annotations

from time import sleep

from textual.notifications import Notification


def test_message() -> None:
    """A notification should not change the message."""
    assert Notification("test").message == "test"


def test_default_title() -> None:
    """A notification with no title should have a empty title."""
    assert Notification("test").title == ""


def test_default_severity_level() -> None:
    """The default severity level should be as expected."""
    assert Notification("test").severity == "information"


def test_default_timeout() -> None:
    """The default timeout should be as expected."""
    assert Notification("test").timeout == Notification.timeout


def test_identity_is_unique() -> None:
    """A collection of notifications should, by default, have unique IDs."""
    notifications: set[str] = set()
    for _ in range(1000):
        notifications.add(Notification("test").identity)
    assert len(notifications) == 1000


def test_time_out() -> None:
    test = Notification("test", timeout=0.5)
    assert test.has_expired is False
    sleep(0.6)
    assert test.has_expired is True
