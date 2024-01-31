import pytest

from textual.app import App, ComposeResult
from textual.reactive import ReactiveError, reactive
from textual.widgets import Label


class FooLabel(Label):
    foo = reactive("Foo")

    def render(self) -> str:
        return self.foo


class DataBindApp(App):
    foo = reactive("Bar")

    def compose(self) -> ComposeResult:
        yield FooLabel(id="label1").data_bind("foo")  # Bind similarly named
        yield FooLabel(id="label2").data_bind(foo=DataBindApp.foo)  # Explicit bind
        yield FooLabel(id="label3")  # Not bound


async def test_data_binding():
    app = DataBindApp()
    async with app.run_test():

        # Check default
        assert app.foo == "Bar"

        label1 = app.query_one("#label1", FooLabel)
        label2 = app.query_one("#label2", FooLabel)
        label3 = app.query_one("#label3", FooLabel)

        # These are bound, so should have the same value as the App.foo
        assert label1.foo == "Bar"
        assert label2.foo == "Bar"
        # Not yet bound, so should have its own default
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


async def test_data_binding_positional_error():

    class DataBindErrorApp(App):
        foo = reactive("Bar")

        def compose(self) -> ComposeResult:
            yield FooLabel(id="label1").data_bind("bar")  # Missing reactive

    app = DataBindErrorApp()
    with pytest.raises(ReactiveError):
        async with app.run_test():
            pass


async def test_data_binding_positional_repeated_error():

    class DataBindErrorApp(App):
        foo = reactive("Bar")

        def compose(self) -> ComposeResult:
            yield FooLabel(id="label1").data_bind(
                "foo", foo=DataBindErrorApp.foo
            )  # Duplicate name

    app = DataBindErrorApp()
    with pytest.raises(ReactiveError):
        async with app.run_test():
            pass


async def test_data_binding_keyword_args_errors():

    class DataBindErrorApp(App):
        foo = reactive("Bar")

        def compose(self) -> ComposeResult:
            yield FooLabel(id="label1").data_bind(
                bar=DataBindErrorApp.foo
            )  # Missing reactive

    app = DataBindErrorApp()
    with pytest.raises(ReactiveError):
        async with app.run_test():
            pass
