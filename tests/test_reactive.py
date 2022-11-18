import asyncio

import pytest

from textual.app import App, ComposeResult
from textual.reactive import reactive
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
            pytest.fail("Async watcher wasn't called within timeout when reactive init = True")

    assert app.count == OLD_VALUE
    assert app.watcher_old_value == OLD_VALUE
    assert app.watcher_new_value == OLD_VALUE  # The value wasn't changed


async def test_watch_init_true():
    class WatcherInitTrue(App):
        count = reactive(OLD_VALUE)
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


@pytest.mark.xfail(reason="Validator methods not running when init=True [issue#1220]")
async def test_validate_init_true():
    """When init is True for a reactive attribute, Textual should call the validator
    AND the watch method when the app starts."""

    class ValidatorInitTrue(App):
        count = reactive(5, init=True)

        def validate_count(self, value: int) -> int:
            return value + 1

    app = ValidatorInitTrue()
    async with app.run_test():
        assert app.count == 6  # Validator should run, so value should be 5+1=6


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


async def test_reactive_method_inheritance():
    """When you override a watch method in a subclass of a widget, Textual will not
    call the superclass watch method for you. Essentially this test is just ensuring
    that normal inheritance rules apply for reactive methods (unlike for event/message handling)
    """
    calls = []

    class Parent(Widget):
        count = reactive(0, init=False)

        def validate_count(self, value: int) -> int:
            calls.append("validate parent")
            return value + 1

        def watch_count(self, value: int) -> None:
            calls.append("watch parent")

    class Child(Parent):
        def watch_count(self, value: int) -> None:
            calls.append("watch child")

    class WatchInheritance(App):
        def compose(self) -> ComposeResult:
            yield Child()

    app = WatchInheritance()
    async with app.run_test():
        child = app.query_one(Child)
        child.count = 1
        assert calls == ["validate parent", "watch child"]
        assert child.count == 2
