from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen


async def test_unmount():
    """Test unmount events are received in reverse DOM order."""
    unmount_ids: list[str] = []

    class UnmountWidget(Container):
        def on_unmount(self, event: events.Unmount):
            unmount_ids.append(
                f"{self.__class__.__name__}#{self.id}-{self.parent is not None}-{len(self._nodes)}"
            )

    class MyScreen(Screen):
        def compose(self) -> ComposeResult:
            yield UnmountWidget(
                UnmountWidget(
                    UnmountWidget(id="bar1"), UnmountWidget(id="bar2"), id="bar"
                ),
                UnmountWidget(
                    UnmountWidget(id="baz1"), UnmountWidget(id="baz2"), id="baz"
                ),
                id="top",
            )

        def on_unmount(self, event: events.Unmount):
            unmount_ids.append(f"{self.__class__.__name__}#{self.id}")

    class UnmountApp(App):
        async def on_mount(self) -> None:
            await self.push_screen(MyScreen(id="main"))

    app = UnmountApp()
    async with app.run_test() as pilot:
        await pilot.exit(None)

    expected = [
        "UnmountWidget#bar1-True-0",
        "UnmountWidget#bar2-True-0",
        "UnmountWidget#baz1-True-0",
        "UnmountWidget#baz2-True-0",
        "UnmountWidget#bar-True-0",
        "UnmountWidget#baz-True-0",
        "UnmountWidget#top-True-0",
        "MyScreen#main",
    ]

    assert unmount_ids == expected
