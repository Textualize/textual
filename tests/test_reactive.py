from __future__ import annotations

import asyncio

import pytest

from textual.app import App, ComposeResult
from textual.message import Message
from textual.message_pump import MessagePump
from textual.reactive import Reactive, TooManyComputesError, reactive, var
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

        with pytest.raises(AttributeError):
            app.count_double = 100


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


async def test_public_and_private_watch() -> None:
    """If a reactive/var has public and private watches both should get called."""

    calls: dict[str, bool] = {"private": False, "public": False}

    class PrivateWatchTest(App):
        counter = var(0, init=False)

        def watch_counter(self) -> None:
            calls["public"] = True

        def _watch_counter(self) -> None:
            calls["private"] = True

    async with PrivateWatchTest().run_test() as pilot:
        assert calls["private"] is False
        assert calls["public"] is False
        pilot.app.counter += 1
        assert calls["private"] is True
        assert calls["public"] is True


async def test_private_validate() -> None:
    calls: dict[str, bool] = {"private": False}

    class PrivateValidateTest(App):
        counter = var(0, init=False)

        def _validate_counter(self, _: int) -> None:
            calls["private"] = True

    async with PrivateValidateTest().run_test() as pilot:
        assert calls["private"] is False
        pilot.app.counter += 1
        assert calls["private"] is True


async def test_public_and_private_validate() -> None:
    """If a reactive/var has public and private validate both should get called."""

    calls: dict[str, bool] = {"private": False, "public": False}

    class PrivateValidateTest(App):
        counter = var(0, init=False)

        def validate_counter(self, _: int) -> None:
            calls["public"] = True

        def _validate_counter(self, _: int) -> None:
            calls["private"] = True

    async with PrivateValidateTest().run_test() as pilot:
        assert calls["private"] is False
        assert calls["public"] is False
        pilot.app.counter += 1
        assert calls["private"] is True
        assert calls["public"] is True


async def test_public_and_private_validate_order() -> None:
    """The private validate should be called first."""

    class ValidateOrderTest(App):
        value = var(0, init=False)

        def validate_value(self, value: int) -> int:
            if value < 0:
                return 42
            return value

        def _validate_value(self, value: int) -> int:
            if value < 0:
                return 73
            return value

    async with ValidateOrderTest().run_test() as pilot:
        pilot.app.value = -10
        assert pilot.app.value == 73


async def test_public_and_private_compute() -> None:
    """If a reactive/var has public and private compute both should get called."""

    with pytest.raises(TooManyComputesError):

        class PublicAndPrivateComputeTest(App):
            counter = var(0, init=False)

            def compute_counter(self):
                pass

            def _compute_counter(self):
                pass


async def test_private_compute() -> None:
    class PrivateComputeTest(App):
        double = var(0, init=False)
        base = var(0, init=False)

        def _compute_double(self) -> int:
            return 2 * self.base

    async with PrivateComputeTest().run_test() as pilot:
        pilot.app.base = 5
        assert pilot.app.double == 10


async def test_async_reactive_watch_callbacks_go_on_the_watcher():
    """Regression test for https://github.com/Textualize/textual/issues/3036.

    This makes sure that async callbacks are called.
    See the next test for sync callbacks.
    """

    from_app = False
    from_holder = False

    class Holder(Widget):
        attr = var(None)

        def watch_attr(self):
            nonlocal from_holder
            from_holder = True

    class MyApp(App):
        def __init__(self):
            super().__init__()
            self.holder = Holder()

        def on_mount(self):
            self.watch(self.holder, "attr", self.callback)

        def update(self):
            self.holder.attr = "hello world"

        async def callback(self):
            nonlocal from_app
            from_app = True

    async with MyApp().run_test() as pilot:
        pilot.app.update()
        await pilot.pause()
        assert from_holder
        assert from_app


async def test_sync_reactive_watch_callbacks_go_on_the_watcher():
    """Regression test for https://github.com/Textualize/textual/issues/3036.

    This makes sure that sync callbacks are called.
    See the previous test for async callbacks.
    """

    from_app = False
    from_holder = False

    class Holder(Widget):
        attr = var(None)

        def watch_attr(self):
            nonlocal from_holder
            from_holder = True

    class MyApp(App):
        def __init__(self):
            super().__init__()
            self.holder = Holder()

        def on_mount(self):
            self.watch(self.holder, "attr", self.callback)

        def update(self):
            self.holder.attr = "hello world"

        def callback(self):
            nonlocal from_app
            from_app = True

    async with MyApp().run_test() as pilot:
        pilot.app.update()
        await pilot.pause()
        assert from_holder
        assert from_app


async def test_set_reactive():
    """Test set_reactive doesn't call watchers."""

    class MyWidget(Widget):
        foo = reactive("")

        def __init__(self, foo: str) -> None:
            super().__init__()
            self.set_reactive(MyWidget.foo, foo)

        def watch_foo(self) -> None:
            # Should never get here
            1 / 0

    class MyApp(App):
        def compose(self) -> ComposeResult:
            yield MyWidget("foobar")

    app = MyApp()
    async with app.run_test():
        assert app.query_one(MyWidget).foo == "foobar"


async def test_no_duplicate_external_watchers() -> None:
    """Make sure we skip duplicated watchers."""

    counter = 0

    class Holder(Widget):
        attr = var(None)

    class MyApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.holder = Holder()

        def on_mount(self) -> None:
            self.watch(self.holder, "attr", self.callback)
            self.watch(self.holder, "attr", self.callback)

        def callback(self) -> None:
            nonlocal counter
            counter += 1

    app = MyApp()
    async with app.run_test():
        assert counter == 1
        app.holder.attr = 73
        assert counter == 2


async def test_external_watch_init_does_not_propagate() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3878.

    Make sure that when setting an extra watcher programmatically and `init` is set,
    we init only the new watcher and not the other ones, but at the same
    time make sure both watchers work in regular circumstances.
    """

    logs: list[str] = []

    class SomeWidget(Widget):
        test_1: var[int] = var(0)
        test_2: var[int] = var(0, init=False)

        def watch_test_1(self) -> None:
            logs.append("test_1")

        def watch_test_2(self) -> None:
            logs.append("test_2")

    class InitOverrideApp(App[None]):
        def compose(self) -> ComposeResult:
            yield SomeWidget()

        def on_mount(self) -> None:
            def watch_test_2_extra() -> None:
                logs.append("test_2_extra")

            self.watch(self.query_one(SomeWidget), "test_2", watch_test_2_extra)

    app = InitOverrideApp()
    async with app.run_test():
        assert logs == ["test_1", "test_2_extra"]
        app.query_one(SomeWidget).test_2 = 73
        assert logs.count("test_2_extra") == 2
        assert logs.count("test_2") == 1


async def test_external_watch_init_does_not_propagate_to_externals() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3878.

    Make sure that when setting an extra watcher programmatically and `init` is set,
    we init only the new watcher and not the other ones (even if they were
    added dynamically with `watch`), but at the same time make sure all watchers
    work in regular circumstances.
    """

    logs: list[str] = []

    class SomeWidget(Widget):
        test_var: var[int] = var(0)

    class MyApp(App[None]):
        def compose(self) -> ComposeResult:
            yield SomeWidget()

        def add_first_watcher(self) -> None:
            def first_callback() -> None:
                logs.append("first")

            self.watch(self.query_one(SomeWidget), "test_var", first_callback)

        def add_second_watcher(self) -> None:
            def second_callback() -> None:
                logs.append("second")

            self.watch(self.query_one(SomeWidget), "test_var", second_callback)

    app = MyApp()
    async with app.run_test():
        assert logs == []
        app.add_first_watcher()
        assert logs == ["first"]
        app.add_second_watcher()
        assert logs == ["first", "second"]
        app.query_one(SomeWidget).test_var = 73
        assert logs == ["first", "second", "first", "second"]


async def test_message_sender_from_reactive() -> None:
    """Test that the sender of a message comes from the reacting widget."""

    message_senders: list[MessagePump | None] = []

    class TestWidget(Widget):
        test_var: var[int] = var(0, init=False)

        class TestMessage(Message):
            pass

        def watch_test_var(self) -> None:
            self.post_message(self.TestMessage())

        def make_reaction(self) -> None:
            self.test_var += 1

    class TestContainer(Widget):
        def compose(self) -> ComposeResult:
            yield TestWidget()

        def on_test_widget_test_message(self, event: TestWidget.TestMessage) -> None:
            nonlocal message_senders
            message_senders.append(event._sender)

    class TestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TestContainer()

    async with TestApp().run_test() as pilot:
        assert message_senders == []
        pilot.app.query_one(TestWidget).make_reaction()
        await pilot.pause()
        assert message_senders == [pilot.app.query_one(TestWidget)]


async def test_mutate_reactive() -> None:
    """Test explicitly mutating reactives"""

    watched_names: list[list[str]] = []

    class TestWidget(Widget):
        names: reactive[list[str]] = reactive(list)

        def watch_names(self, names: list[str]) -> None:
            watched_names.append(names.copy())

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield TestWidget()

    app = TestApp()
    async with app.run_test():
        widget = app.query_one(TestWidget)
        # watch method called on startup
        assert watched_names == [[]]

        # Mutate the list
        widget.names.append("Paul")
        # No changes expected
        assert watched_names == [[]]
        # Explicitly mutate the reactive
        widget.mutate_reactive(TestWidget.names)
        # Watcher will be invoked
        assert watched_names == [[], ["Paul"]]
        # Make further modifications
        widget.names.append("Jessica")
        widget.names.remove("Paul")
        # No change expected
        assert watched_names == [[], ["Paul"]]
        # Explicit mutation
        widget.mutate_reactive(TestWidget.names)
        # Watcher should be invoked
        assert watched_names == [[], ["Paul"], ["Jessica"]]


async def test_mutate_reactive_data_bind() -> None:
    """https://github.com/Textualize/textual/issues/4825"""

    # Record mutations to TestWidget.messages
    widget_messages: list[list[str]] = []

    class TestWidget(Widget):
        messages: reactive[list[str]] = reactive(list, init=False)

        def watch_messages(self, names: list[str]) -> None:
            widget_messages.append(names.copy())

    class TestApp(App):
        messages: reactive[list[str]] = reactive(list, init=False)

        def compose(self) -> ComposeResult:
            yield TestWidget().data_bind(TestApp.messages)

    app = TestApp()
    async with app.run_test():
        test_widget = app.query_one(TestWidget)
        assert widget_messages == [[]]
        assert test_widget.messages == []

        # Should be the same instance
        assert app.messages is test_widget.messages

        # Mutate app
        app.messages.append("foo")
        # Mutations aren't detected
        assert widget_messages == [[]]
        assert app.messages == ["foo"]
        assert test_widget.messages == ["foo"]
        # Explicitly mutate app reactive
        app.mutate_reactive(TestApp.messages)
        # Mutating app, will also invoke watchers on any data binds
        assert widget_messages == [[], ["foo"]]
        assert app.messages == ["foo"]
        assert test_widget.messages == ["foo"]
