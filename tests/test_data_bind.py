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

        yield FooLabel(id="label3")


async def test_data_binding():
    app = DataBindApp()
    async with app.run_test() as pilot:

        # Check default
        assert app.foo == "Bar"

        label1 = app.query_one("#label1", FooLabel)
        label2 = app.query_one("#label2", FooLabel)
        label3 = app.query_one("#label3", FooLabel)

        assert label1.foo == "Foo"
        assert label2.foo == "Foo"
        assert label3.foo == "Foo"

        # Changing this reactive, should also change the bound widgets
        app.foo = "Baz"

        # Sanity check
        assert app.foo == "Baz"

        # Should also have updated bound labels
        assert label1.foo == "Baz"
        assert label2.foo == "Baz"
        assert label3.foo == "Foo"

        # Bind data outside of compose
        label3.data_bind(foo=DataBindApp.foo)
        # Confirm new binding has propagated
        assert label3.foo == "Baz"

        # Set reactive and check propagation
        app.foo = "Egg"
        assert label1.foo == "Egg"
        assert label2.foo == "Egg"
        assert label3.foo == "Egg"

        # Test nothing goes awry when removing widget with bound data
        await label1.remove()

        # Try one last time
        app.foo = "Spam"

        # Confirm remaining widgets still propagate
        assert label2.foo == "Spam"
        assert label3.foo == "Spam"
