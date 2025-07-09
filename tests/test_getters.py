import pytest

from textual import containers, getters
from textual.app import App, ComposeResult
from textual.css.query import NoMatches, WrongType
from textual.widget import Widget
from textual.widgets import Input, Label


async def test_getters() -> None:
    """Check the getter descriptors work, and return expected errors."""

    class QueryApp(App):
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

    app = QueryApp()
    async with app.run_test():

        assert isinstance(app.label1, Label)
        assert app.label1.id == "label1"

        assert isinstance(app.label2, Label)
        assert app.label2.id == "label2"

        with pytest.raises(WrongType):
            app.label1_broken

        with pytest.raises(WrongType):
            app.label2_broken

        with pytest.raises(NoMatches):
            app.label1_missing

        with pytest.raises(NoMatches):
            app.label2_missing
