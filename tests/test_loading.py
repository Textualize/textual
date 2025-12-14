from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, Static


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


async def test_premature_loading():
    """Test a widget can set the `loading` attribute before mounting."""

    # No assert, we're just expecting it to not crash

    class LoadingWidget(Static):
        """A widget that shows a loading indicator."""

    class LoadingApp(App[None]):
        """Simple app with a single loading widget."""

        def compose(self) -> ComposeResult:
            """Compose the app with the loading widget."""
            widget = LoadingWidget("Loading content...")
            widget.loading = True  # Should not crash
            yield widget

    app = LoadingApp()
    async with app.run_test() as pilot:
        await pilot.pause()
