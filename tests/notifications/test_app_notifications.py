from time import sleep

from textual.app import App


class NotificationApp(App[None]):
    pass


async def test_app_no_notifications() -> None:
    """An app with no notifications should have an empty notification list."""
    async with NotificationApp().run_test() as pilot:
        assert len(pilot.app._notifications) == 0


async def test_app_with_notifications() -> None:
    """An app with notifications should have notifications in the list."""
    async with NotificationApp().run_test() as pilot:
        pilot.app.notify("test")
        assert len(pilot.app._notifications) == 1


async def test_app_with_notifications_that_expire() -> None:
    """Notifications should expire from an app."""
    async with NotificationApp().run_test() as pilot:
        for n in range(100):
            pilot.app.notify("test", timeout=(0.5 if bool(n % 2) else 60))
        assert len(pilot.app._notifications) == 100
        sleep(0.6)
        assert len(pilot.app._notifications) == 50
