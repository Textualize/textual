"""Test that setting a toggle button's label has the desired effect."""

from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Checkbox, RadioButton, RadioSet


class LabelChangeApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Checkbox("Before")
        yield RadioButton("Before")
        yield RadioSet("Before")


async def test_change_labels() -> None:
    """It should be possible to change the labels of toggle buttons."""
    async with LabelChangeApp().run_test() as pilot:
        assert pilot.app.query_one(Checkbox).label == Text("Before")
        assert pilot.app.query_one("Screen > RadioButton", RadioButton).label == Text(
            "Before"
        )
        assert pilot.app.query_one("RadioSet > RadioButton", RadioButton).label == Text(
            "Before"
        )
        pilot.app.query_one(Checkbox).label = "After"
        pilot.app.query_one("Screen > RadioButton", RadioButton).label = "After"
        pilot.app.query_one("RadioSet > RadioButton", RadioButton).label = "After"
        await pilot.pause()
        assert pilot.app.query_one(Checkbox).label == Text("After")
        assert pilot.app.query_one("Screen > RadioButton", RadioButton).label == Text(
            "After"
        )
        assert pilot.app.query_one("RadioSet > RadioButton", RadioButton).label == Text(
            "After"
        )
