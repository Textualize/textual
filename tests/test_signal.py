import pytest

from textual.app import App, ComposeResult
from textual.signal import Signal, SignalError
from textual.widgets import Label


async def test_signal():
    """Test signal subscribe"""
    called = 0

    class TestLabel(Label):
        def on_mount(self) -> None:
            def signal_result(_):
                nonlocal called
                called += 1

            assert isinstance(self.app, TestApp)
            self.app.test_signal.subscribe(self, signal_result)

    class TestApp(App):
        BINDINGS = [("space", "signal")]

        def __init__(self) -> None:
            self.test_signal: Signal[str] = Signal(self, "coffee ready")
            super().__init__()

        def compose(self) -> ComposeResult:
            yield TestLabel()

        def action_signal(self) -> None:
            self.test_signal.publish("foo")

    app = TestApp()
    async with app.run_test() as pilot:
        # Check default called is 0
        assert called == 0
        # Action should publish signal
        await pilot.press("space")
        assert called == 1
        # Check a second time
        await pilot.press("space")
        assert called == 2
        # Removed the owner object
        await app.query_one(TestLabel).remove()
        # Check nothing is called
        await pilot.press("space")
        assert called == 2
        # Add a new test label
        await app.mount(TestLabel())
        # Check callback again
        await pilot.press("space")
        assert called == 3
        # Unsubscribe
        app.test_signal.unsubscribe(app.query_one(TestLabel))
        # Check nothing to update
        await pilot.press("space")
        assert called == 3


def test_signal_errors():
    """Check exceptions raised by Signal class."""
    app = App()
    test_signal = Signal(app, "test")
    label = Label()
    # Check subscribing a non-running widget is an error
    with pytest.raises(SignalError):
        test_signal.subscribe(label, lambda _: None)


def test_repr():
    """Check the repr doesn't break."""
    app = App()
    test_signal = Signal(app, "test")
    assert isinstance(repr(test_signal), str)


async def test_signal_parameters():
    str_result: str | None = None
    int_result: int | None = None

    class TestApp(App):
        BINDINGS = [("space", "signal")]

        def __init__(self) -> None:
            self.str_signal: Signal[str] = Signal(self, "str")
            self.int_signal: Signal[int] = Signal(self, "int")
            super().__init__()

        def action_signal(self) -> None:
            self.str_signal.publish("foo")
            self.int_signal.publish(3)

        def on_mount(self) -> None:
            def on_str(my_str):
                nonlocal str_result
                str_result = my_str

            def on_int(my_int):
                nonlocal int_result
                int_result = my_int

            self.str_signal.subscribe(self, on_str)
            self.int_signal.subscribe(self, on_int)

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.press("space")
        assert str_result == "foo"
        assert int_result == 3
