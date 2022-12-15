import asyncio

import pytest

from textual.app import App
from textual.reactive import reactive, var

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
                "Async watcher wasn't called within timeout when reactive init = True")

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
        # TODO: Commented out below due to issue#1230, should work after issue fixed
        # Value is the same, and always_update=False, so watcher NOT called...
        # app.last_name = "Burns"
        # assert calls == ["first_name Darren"]
        # Values changed, watch method always called regardless of always_update
        app.first_name = "abc"
        app.last_name = "def"
        assert calls == ["first_name Darren", "first_name abc", "last_name def"]


async def test_reactive_with_callable_default():
    """A callable can be supplied as the default value for a reactive.
    Textual will call it in order to retrieve the default value."""
    called_with_app = None

    def set_called(app: App) -> int:
        nonlocal called_with_app
        called_with_app = app
        return OLD_VALUE

    class ReactiveCallable(App):
        value = reactive(set_called)
        watcher_called_with = None

        def watch_value(self, new_value):
            self.watcher_called_with = new_value

    app = ReactiveCallable()
    async with app.run_test():
        assert app.value == OLD_VALUE  # The value should be set to the return val of the callable
    assert called_with_app is app  # Ensure the App is passed into the reactive default callable
    assert app.watcher_called_with == OLD_VALUE


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



@pytest.mark.xfail(reason="Compute methods not called when init=True [issue#1227]")
async def test_reactive_compute_first_time_set():
    class ReactiveComputeFirstTimeSet(App):
        number = reactive(1)
        double_number = reactive(None)

        def compute_double_number(self):
            return self.number * 2

    app = ReactiveComputeFirstTimeSet()
    async with app.run_test():
        await asyncio.sleep(.2)  # TODO: We sleep here while issue#1218 is open
        assert app.double_number == 2


@pytest.mark.xfail(reason="Compute methods not called immediately [issue#1218]")
async def test_reactive_method_call_order():
    class CallOrder(App):
        count = reactive(OLD_VALUE, init=False)
        count_times_ten = reactive(OLD_VALUE * 10)
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
