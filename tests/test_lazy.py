from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.lazy import Lazy
from textual.widgets import Label


class LazyApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Lazy(Horizontal()):
                yield Label(id="foo")
            with Horizontal():
                yield Label(id="bar")


async def test_lazy():
    app = LazyApp()
    async with app.run_test() as pilot:
        # No #foo on initial mount
        assert len(app.query("#foo")) == 0
        assert len(app.query("#bar")) == 1
        await pilot.pause()
        await pilot.pause()
        # #bar mounted after refresh
        assert len(app.query("#foo")) == 1
        assert len(app.query("#bar")) == 1
