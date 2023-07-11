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
