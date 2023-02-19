import asyncio

import pytest

from textual.app import App, ComposeResult
from textual.reactive import Reactive, reactive, var
from textual.widget import Widget

OLD_VALUE = 5_000
NEW_VALUE = 1_000_000


async def test_watch():
    """Test that changes to a watched reactive attribute happen immediately."""

    class WatchApp(App):
        count = reactive(0, init=False)

        watcher_call_count = 0

        def watch_count(self, value: int) -> None:
            self.watcher_call_count = value

    app = WatchApp()
    async with app.run_test():
        app.count += 1
        assert app.watcher_call_count == 1
        app.count += 1
        assert app.watcher_call_count == 2
        app.count -= 1
        assert app.watcher_call_count == 1
        app.count -= 1
        assert app.watcher_call_count == 0


async def test_watch_async_init_false():
    """Ensure that async watchers are called eventually when set by user code"""

    class WatchAsyncApp(App):
        count = reactive(OLD_VALUE, init=False)
        watcher_old_value = None
        watcher_new_value = None
        watcher_called_event = asyncio.Event()

        async def watch_count(self, old_value: int, new_value: int) -> None:
            self.watcher_old_value = old_value
            self.watcher_new_value = new_value
            self.watcher_called_event.set()

    app = WatchAsyncApp()
    async with app.run_test():
        app.count = NEW_VALUE
        assert app.count == NEW_VALUE  # Value is set immediately
        try:
            await asyncio.wait_for(app.watcher_called_event.wait(), timeout=0.05)
        except TimeoutError:
            pytest.fail("Async watch method (watch_count) wasn't called within timeout")

        assert app.count == NEW_VALUE  # Sanity check
        assert app.watcher_old_value == OLD_VALUE  # old_value passed to watch method
        assert app.watcher_new_value == NEW_VALUE  # new_value passed to watch method


async def test_watch_async_init_true():
    """Ensure that when init is True in a reactive, its async watcher gets called
    by Textual eventually, even when the user does not set the value themselves."""

    class WatchAsyncApp(App):
        count = reactive(OLD_VALUE, init=True)
        watcher_called_event = asyncio.Event()
        watcher_old_value = None
        watcher_new_value = None

        async def watch_count(self, old_value: int, new_value: int) -> None:
            self.watcher_old_value = old_value
            self.watcher_new_value = new_value
            self.watcher_called_event.set()

    app = WatchAsyncApp()
    async with app.run_test():
        try:
            await asyncio.wait_for(app.watcher_called_event.wait(), timeout=0.05)
        except TimeoutError:
            pytest.fail(
                "Async watcher wasn't called within timeout when reactive init = True"
            )

    assert app.count == OLD_VALUE
    assert app.watcher_old_value == OLD_VALUE
    assert app.watcher_new_value == OLD_VALUE  # The value wasn't changed


async def test_watch_init_false_always_update_false():
    class WatcherInitFalse(App):
        count = reactive(0, init=False)
        watcher_call_count = 0

        def watch_count(self, new_value: int) -> None:
            self.watcher_call_count += 1

    app = WatcherInitFalse()
    async with app.run_test():
        app.count = 0  # Value hasn't changed, and always_update=False, so watch_count shouldn't run
        assert app.watcher_call_count == 0
        app.count = 0
        assert app.watcher_call_count == 0
        app.count = 1
        assert app.watcher_call_count == 1


async def test_watch_init_true():
    class WatcherInitTrue(App):
        count = var(OLD_VALUE)
        watcher_call_count = 0

        def watch_count(self, new_value: int) -> None:
            self.watcher_call_count += 1

    app = WatcherInitTrue()
    async with app.run_test():
        assert app.count == OLD_VALUE
        assert app.watcher_call_count == 1  # Watcher called on init
        app.count = NEW_VALUE  # User sets the value...
        assert app.watcher_call_count == 2  # ...resulting in 2nd call
        app.count = NEW_VALUE  # Setting to the SAME value
        assert app.watcher_call_count == 2  # Watcher is NOT called again


async def test_reactive_always_update():
    calls = []

    class AlwaysUpdate(App):
        first_name = reactive("Darren", init=False, always_update=True)
        last_name = reactive("Burns", init=False)

        def watch_first_name(self, value):
            calls.append(f"first_name {value}")

        def watch_last_name(self, value):
            calls.append(f"last_name {value}")

    app = AlwaysUpdate()
    async with app.run_test():
        # Value is the same, but always_update=True, so watcher called...
        app.first_name = "Darren"
        assert calls == ["first_name Darren"]
        # Value is the same, and always_update=False, so watcher NOT called...
        app.last_name = "Burns"
        assert calls == ["first_name Darren"]
        # Values changed, watch method always called regardless of always_update
        app.first_name = "abc"
        app.last_name = "def"
        assert calls == ["first_name Darren", "first_name abc", "last_name def"]


async def test_reactive_with_callable_default():
    """A callable can be supplied as the default value for a reactive.
    Textual will call it in order to retrieve the default value."""

    class ReactiveCallable(App):
        value = reactive(lambda: 123)
        watcher_called_with = None

        def watch_value(self, new_value):
            self.watcher_called_with = new_value

    app = ReactiveCallable()
    async with app.run_test():
        assert app.value == 123
        assert app.watcher_called_with == 123


async def test_validate_init_true():
    """When init is True for a reactive attribute, Textual should call the validator
    AND the watch method when the app starts."""
    validator_call_count = 0

    class ValidatorInitTrue(App):
        count = var(5, init=True)

        def validate_count(self, value: int) -> int:
            nonlocal validator_call_count
            validator_call_count += 1
            return value + 1

    app = ValidatorInitTrue()
    async with app.run_test():
        app.count = 5
        assert app.count == 6  # Validator should run, so value should be 5+1=6
        assert validator_call_count == 1


async def test_validate_init_true_set_before_dom_ready():
    """When init is True for a reactive attribute, Textual should call the validator
    AND the watch method when the app starts."""
    validator_call_count = 0

    class ValidatorInitTrue(App):
        count = var(5, init=True)

        def validate_count(self, value: int) -> int:
            nonlocal validator_call_count
            validator_call_count += 1
            return value + 1

    app = ValidatorInitTrue()
    app.count = 5
    async with app.run_test():
        assert app.count == 6  # Validator should run, so value should be 5+1=6
        assert validator_call_count == 1


async def test_reactive_compute_first_time_set():
    class ReactiveComputeFirstTimeSet(App):
        number = reactive(1)
        double_number = reactive(None)

        def compute_double_number(self):
            return self.number * 2

    app = ReactiveComputeFirstTimeSet()
    async with app.run_test():
        assert app.double_number == 2


async def test_reactive_method_call_order():
    class CallOrder(App):
        count = reactive(OLD_VALUE, init=False)
        count_times_ten = reactive(OLD_VALUE * 10, init=False)
        calls = []

        def validate_count(self, value: int) -> int:
            self.calls.append(f"validate {value}")
            return value + 1

        def watch_count(self, value: int) -> None:
            self.calls.append(f"watch {value}")

        def compute_count_times_ten(self) -> int:
            self.calls.append(f"compute {self.count}")
            return self.count * 10

    app = CallOrder()
    async with app.run_test():
        app.count = NEW_VALUE
        assert app.calls == [
            # The validator receives NEW_VALUE, since that's what the user
            # set the reactive attribute to...
            f"validate {NEW_VALUE}",
            # The validator adds 1 to the new value, and this is what should
            # be passed into the watcher...
            f"watch {NEW_VALUE + 1}",
            # The compute method accesses the reactive value directly, which
            # should have been updated by the validator to NEW_VALUE + 1.
            f"compute {NEW_VALUE + 1}",
        ]
        assert app.count == NEW_VALUE + 1
        assert app.count_times_ten == (NEW_VALUE + 1) * 10


async def test_premature_reactive_call():
    watcher_called = False

    class BrokenWidget(Widget):
        foo = reactive(1)

        def __init__(self) -> None:
            super().__init__()
            self.foo = "bar"

        async def watch_foo(self) -> None:
            nonlocal watcher_called
            watcher_called = True

    class PrematureApp(App):
        def compose(self) -> ComposeResult:
            yield BrokenWidget()

    app = PrematureApp()
    async with app.run_test() as pilot:
        assert watcher_called
        app.exit()


async def test_reactive_inheritance():
    """Check that inheritance works as expected for reactives."""

    class Primary(App):
        foo = reactive(1)
        bar = reactive("bar")

    class Secondary(Primary):
        foo = reactive(2)
        egg = reactive("egg")

    class Tertiary(Secondary):
        baz = reactive("baz")

    from rich import print

    primary = Primary()
    secondary = Secondary()
    tertiary = Tertiary()

    primary_reactive_count = len(primary._reactives)

    # Secondary adds one new reactive
    assert len(secondary._reactives) == primary_reactive_count + 1

    Reactive._initialize_object(primary)
    Reactive._initialize_object(secondary)
    Reactive._initialize_object(tertiary)

    # Primary doesn't have egg
    with pytest.raises(AttributeError):
        assert primary.egg

    # primary has foo of 1
    assert primary.foo == 1
    # secondary has different reactive
    assert secondary.foo == 2
    # foo is accessible through tertiary
    assert tertiary.foo == 2

    with pytest.raises(AttributeError):
        secondary.baz

    assert tertiary.baz == "baz"


async def test_compute():
    """Check compute method is called."""

    class ComputeApp(App):
        count = var(0)
        count_double = var(0)

        def __init__(self) -> None:
            self.start = 0
            super().__init__()

        def compute_count_double(self) -> int:
            return self.start + self.count * 2

    app = ComputeApp()

    async with app.run_test():
        assert app.count_double == 0
        app.count = 1
        assert app.count_double == 2
        assert app.count_double == 2
        app.count = 2
        assert app.count_double == 4
        app.start = 10
        assert app.count_double == 14


async def test_watch_compute():
    """Check that watching a computed attribute works."""

    watch_called: list[bool] = []

    class Calculator(App):
        numbers = var("0")
        show_ac = var(True)
        value = var("")

        def compute_show_ac(self) -> bool:
            return self.value in ("", "0") and self.numbers == "0"

        def watch_show_ac(self, show_ac: bool) -> None:
            """Called when show_ac changes."""
            watch_called.append(show_ac)

    app = Calculator()

    # Referencing the value calls compute
    # Setting any reactive values calls compute
    async with app.run_test():
        assert app.show_ac is True
        app.value = "1"
        assert app.show_ac is False
        app.value = "0"
        assert app.show_ac is True
        app.numbers = "123"
        assert app.show_ac is False

    assert watch_called == [True, True, False, False, True, True, False, False]
