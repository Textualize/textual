from textual.app import App
from textual.widgets import Label


class SelfRemovingLabel(Label):
    async def on_mount(self) -> None:
        await self.remove()


class RemoveOnTimerApp(App[None]):
    def on_mount(self):
        for _ in range(5):
            self.mount(SelfRemovingLabel("I will remove myself!"))


async def test_multiple_simultaneous_removals():
    """Regression test for https://github.com/Textualize/textual/issues/2854."""
    # The app should run and finish without raising any errors.
    async with RemoveOnTimerApp().run_test() as pilot:
        # Sanity check to ensure labels were removed.
        assert len(pilot.app.query(Label)) == 0
