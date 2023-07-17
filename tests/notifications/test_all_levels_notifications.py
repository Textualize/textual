from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget


class NotifyWidget(Widget):
    def on_mount(self) -> None:
        self.notify("test", timeout=60)


class NotifyScreen(Screen):
    def on_mount(self) -> None:
        self.notify("test", timeout=60)

    def compose(self) -> ComposeResult:
        yield NotifyWidget()


class NotifyApp(App[None]):
    def on_mount(self) -> None:
        self.notify("test", timeout=60)
        self.push_screen(NotifyScreen())


async def test_all_levels_of_notification() -> None:
    """All levels within the DOM should be able to notify."""
    async with NotifyApp().run_test() as pilot:
        assert len(pilot.app._notifications) == 3
