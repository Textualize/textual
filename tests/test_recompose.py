from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label


async def test_recompose_preserve_id():
    """Check recomposing leaves widgets with matching ID."""

    class MyVertical(Vertical):
        def compose(self) -> ComposeResult:
            yield Label("foo", classes="foo", name="foo")
            yield Input(id="bar", name="bar")
            yield Label("baz", classes="baz", name="baz")

    class RecomposeApp(App):
        def compose(self) -> ComposeResult:
            yield MyVertical()

    app = RecomposeApp()
    async with app.run_test() as pilot:
        foo = app.query_one(".foo")
        bar = app.query_one("#bar")
        baz = app.query_one(".baz")
        assert [node.name for node in app.query("MyVertical > *")] == [
            "foo",
            "bar",
            "baz",
        ]

        bar.focus()
        await pilot.press("h", "i")
        await app.query_one(MyVertical).recompose()

        # Order shouldn't change
        assert [node.name for node in app.query("MyVertical > *")] == [
            "foo",
            "bar",
            "baz",
        ]

        # Check that only the ID is the same instance
        assert app.query_one(".foo") is not foo  # New instance
        assert app.query_one("#bar") is bar  # Matching id, so old instance
        assert app.query_one(".baz") is not baz  # new instance

        assert app.query_one("#bar", Input).value == "hi"
