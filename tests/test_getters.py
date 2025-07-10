import pytest

from textual import containers, getters
from textual.app import App, ComposeResult
from textual.css.query import NoMatches, WrongType
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Input, Label


async def test_getters() -> None:
    """Check the getter descriptors work, and return expected errors."""

    class GetterScreen(Screen):
        label1 = getters.query_one("#label1", Label)
        label2 = getters.child_by_id("label2", Label)
        label1_broken = getters.query_one("#label1", Input)
        label2_broken = getters.child_by_id("label2", Input)
        label1_missing = getters.query_one("#foo", Widget)
        label2_missing = getters.child_by_id("bar", Widget)

        def compose(self) -> ComposeResult:
            with containers.Vertical():
                yield Label(id="label1", classes="red")
            yield Label(id="label2", classes="green")

    class QueryApp(App):

        def get_default_screen(self) -> Screen:
            return GetterScreen()

    app = QueryApp()
    async with app.run_test():
        screen: GetterScreen = app.screen

        assert isinstance(screen.label1, Label)
        assert screen.label1.id == "label1"

        assert isinstance(screen.label2, Label)
        assert screen.label2.id == "label2"

        with pytest.raises(WrongType):
            screen.label1_broken

        with pytest.raises(WrongType):
            screen.label2_broken

        with pytest.raises(NoMatches):
            screen.label1_missing

        with pytest.raises(NoMatches):
            screen.label2_missing
