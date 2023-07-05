from textual.app import App
from textual.widgets import Label


class SelfRemovingLabel(Label):
    def on_mount(self) -> None:
        self.set_timer(0.2, self.remove)


class RemoveOnTimerApp(App[None]):
    def on_mount(self):
        for _ in range(5):
            self.mount(SelfRemovingLabel("I will remove myself!"))


async def test_multiple_simultaneous_removals():
    """Regression test for https://github.com/Textualize/textual/issues/2854."""
    # The app should run and finish without raising any errors.
    async with RemoveOnTimerApp().run_test() as pilot:
        await pilot.pause(0.3)
        # Sanity check to ensure labels were removed.
        assert len(pilot.app.query(Label)) == 0
