from __future__ import annotations

from time import sleep

from textual.notifications import Notification, Notifications


def test_empty_to_start_with() -> None:
    """We should have no notifications if we've not raised any."""
    assert len(Notifications()) == 0


def test_many_notifications() -> None:
    """Adding lots of long-timeout notifications should result in them being in the list."""
    tester = Notifications()
    for _ in range(100):
        tester.add(Notification("test", timeout=60))
    assert len(tester) == 100


def test_timeout() -> None:
    """Notifications should timeout from the list."""
    tester = Notifications()
    for n in range(100):
        tester.add(Notification("test", timeout=(0.5 if bool(n % 2) else 60)))
    assert len(tester) == 100
    sleep(0.6)
    assert len(tester) == 50


def test_in() -> None:
    """It should be possible to test if a notification is in a collection."""
    tester = Notifications()
    within = Notification("within", timeout=120)
    outwith = Notification("outwith", timeout=120)
    tester.add(within)
    assert within in tester
    assert outwith not in tester


def test_remove_notification() -> None:
    """It should be possible to remove a notification."""
    tester = Notifications()
    first = Notification("first", timeout=120)
    second = Notification("second", timeout=120)
    third = Notification("third", timeout=120)
    tester.add(first)
    tester.add(second)
    tester.add(third)
    assert list(tester) == [first, second, third]
    del tester[second]
    assert list(tester) == [first, third]
    del tester[first]
    assert list(tester) == [third]
    del tester[third]
    assert list(tester) == []


def test_remove_notification_multiple_times() -> None:
    """It should be possible to remove the same notification more than once without an error."""
    tester = Notifications()
    alert = Notification("delete me")
    tester.add(alert)
    assert list(tester) == [alert]
    del tester[alert]
    assert list(tester) == []
    del tester[alert]
    assert list(tester) == []


def test_clear() -> None:
    """It should be possible to clear all notifications."""
    tester = Notifications()
    for _ in range(100):
        tester.add(Notification("test", timeout=120))
    assert len(tester) == 100
    tester.clear()
    assert len(tester) == 0
