from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label


class LoadingApp(App[None]):
    CSS = """
    VerticalScroll {
        height: 20;
    }
    """

    BINDINGS = [("l", "loading")]

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("another big label\n" * 30)  # Ensure there's a scrollbar.

    def action_loading(self):
        self.query_one(VerticalScroll).loading = True


async def test_loading_disables_and_remove_scrollbars():
    app = LoadingApp()
    async with app.run_test() as pilot:
        vs = app.query_one(VerticalScroll)
        # Sanity checks:
        assert not vs._check_disabled()

        await pilot.press("l")
        await pilot.pause()

        assert vs._check_disabled()
