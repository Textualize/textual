from textual.app import App, ComposeResult
from textual.reactive import reactive


class WatchApp(App):

    count = reactive(0, init=False)

    test_count = 0

    def watch_count(self, value: int) -> None:
        self.test_count = value


async def test_watch():
    """Test that changes to a watched reactive attribute happen immediately."""
    app = WatchApp()
    async with app.run_test():
        app.count += 1
        assert app.test_count == 1
        app.count += 1
        assert app.test_count == 2
        app.count -= 1
        assert app.test_count == 1
        app.count -= 1
        assert app.test_count == 0
