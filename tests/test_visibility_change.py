"""See https://github.com/Textualize/textual/issues/1355 as the motivation for these tests."""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget


class VisibleTester(App[None]):
    """An app for testing visibility changes."""

    CSS = """
    Widget {
        height: 1fr;
    }
    .hidden {
        visibility: hidden;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Widget(id="keep"), Widget(id="hide-via-code"), Widget(id="hide-via-css")
        )


async def test_visibility_changes() -> None:
    """Test changing visibility via code and CSS."""
    async with VisibleTester().run_test() as pilot:
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is True
        assert pilot.app.query_one("#hide-via-css").visible is True

        pilot.app.query_one("#hide-via-code").styles.visibility = "hidden"
        await pilot.pause(0)
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is False
        assert pilot.app.query_one("#hide-via-css").visible is True

        pilot.app.query_one("#hide-via-css").set_class(True, "hidden")
        await pilot.pause(0)
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is False
        assert pilot.app.query_one("#hide-via-css").visible is False
