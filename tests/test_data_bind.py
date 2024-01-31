from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Label


class FooLabel(Label):
    foo = reactive("Foo")

    def render(self) -> str:
        return self.foo


class DataBindApp(App):
    foo = reactive("Bar", init=False)

    def compose(self) -> ComposeResult:
        yield FooLabel(id="label1").data_bind("foo")
        yield FooLabel(id="label2").data_bind(foo=DataBindApp.foo)


async def test_data_binding():
    app = DataBindApp()
    async with app.run_test() as pilot:

        assert app.foo == "Bar"

        label1 = app.query_one("#label1", FooLabel)
        label2 = app.query_one("#label2", FooLabel)
        assert label1.foo == "Foo"
        assert label2.foo == "Foo"

        # Changing this reactive, should also change the bound widgets
        app.foo = "Baz"

        # Sanity check
        assert app.foo == "Baz"

        # Should also have updated bound labels
        assert label1.foo == "Baz"
        assert label2.foo == "Baz"
