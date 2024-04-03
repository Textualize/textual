import pytest

from textual.app import App, ComposeResult
from textual.reactive import ReactiveError, reactive
from textual.widgets import Label


class FooLabel(Label):
    foo = reactive("Foo")

    def render(self) -> str:
        return self.foo


class DataBindApp(App):
    bar = reactive("Bar")

    def compose(self) -> ComposeResult:
        yield FooLabel(id="label1").data_bind(foo=DataBindApp.bar)
        yield FooLabel(id="label2")  # Not bound


async def test_data_binding():
    app = DataBindApp()
    async with app.run_test() as pilot:

        # Check default
        assert app.bar == "Bar"

        label1 = app.query_one("#label1", FooLabel)
        label2 = app.query_one("#label2", FooLabel)

        # These are bound, so should have the same value as the App.foo
        assert label1.foo == "Bar"
        # Not yet bound, so should have its own default
        assert label2.foo == "Foo"

        # Changing this reactive, should also change the bound widgets
        app.bar = "Baz"

        # Sanity check
        assert app.bar == "Baz"

        # Should also have updated bound labels
        assert label1.foo == "Baz"
        assert label2.foo == "Foo"

        with pytest.raises(ReactiveError):
            # This should be an error because FooLabel.foo is not defined on the app
            label2.data_bind(foo=FooLabel.foo)

        # Bind data outside of compose
        label2.data_bind(foo=DataBindApp.bar)
        await pilot.pause()
        # Confirm new binding has propagated
        assert label2.foo == "Baz"

        # Set reactive and check propagation
        app.bar = "Egg"
        assert label1.foo == "Egg"
        assert label2.foo == "Egg"

        # Test nothing goes awry when removing widget with bound data
        await label1.remove()

        # Try one last time
        app.bar = "Spam"

        # Confirm remaining widgets still propagate
        assert label2.foo == "Spam"


async def test_data_binding_missing_reactive():

    class DataBindErrorApp(App):
        foo = reactive("Bar")

        def compose(self) -> ComposeResult:
            yield FooLabel(id="label1").data_bind(
                nofoo=DataBindErrorApp.foo
            )  # Missing reactive

    app = DataBindErrorApp()
    with pytest.raises(ReactiveError):
        async with app.run_test():
            pass
