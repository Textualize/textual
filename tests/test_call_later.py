import asyncio

from textual.app import App


class CallLaterApp(App[None]):
    def __init__(self) -> None:
        self.display_count = 0
        super().__init__()

    def post_display_hook(self) -> None:
        self.display_count += 1


async def test_call_later() -> None:
    """Check that call later makes a call."""
    app = CallLaterApp()
    called_event = asyncio.Event()

    async with app.run_test():
        app.call_later(called_event.set)
        await asyncio.wait_for(called_event.wait(), 1)


async def test_call_after_refresh() -> None:
    """Check that call later makes a call after a refresh."""
    app = CallLaterApp()

    display_count = -1

    called_event = asyncio.Event()

    def callback() -> None:
        nonlocal display_count
        called_event.set()
        display_count = app.display_count

    async with app.run_test():
        app.call_after_refresh(callback)
        await asyncio.wait_for(called_event.wait(), 1)
        app_display_count = app.display_count
        assert app_display_count > display_count
