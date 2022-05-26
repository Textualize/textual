import pytest

from tests.utilities.test_app import AppTest
from textual.events import Key


@pytest.mark.asyncio
async def test_key_binding_expressions():
    # N.B. This test would have been a bit more elegant modelised as a parameterised test,
    # but as it takes a few milliseconds to boot an instance of AppTest let's be pragmatic
    # and boot it only once - and then, test our various cases against this one instance.

    class MyApp(AppTest):
        key_binding_result = None

        def on_mount(self) -> None:
            bindings = {
                "h": "no_params",
                "s": "static_param('this is a static param')",
                "m": "multiple_static_params('correct horse', 'battery staple')",
                "c": "multiple_static_params_with_capture_all_args(1, 'a', {0: 1e5}, True, [2, 3])",
                "a": "multiple_with_only_capture_all_args(-1, 3.14, None)",
                "0,1,2": "dynamic_param('$event.key')",
                "5,6": "dynamic_and_static_params('$event.key', {'key': 'static value'})",
                # Note that for this example some of our dynamic params will be resolved with single quotes in
                # their string-ified representation, so we'd better use double quotes to wrap them:
                "8,9": """multiple_with_only_capture_all_args("$event.sender", $event.is_forwarded, 'static', "$event.key", '$event.__module__', "$event.__class__.__mro__")""",
            }
            for key, action in bindings.items():
                self.bind(key, action)

        def action_no_params(self) -> None:
            self.key_binding_result = "hello_world"

        def action_static_param(self, received_static_param: str) -> None:
            self.key_binding_result = received_static_param

        def action_multiple_static_params(self, arg_a, arg_b) -> None:
            self.key_binding_result = (arg_a, arg_b)

        def action_multiple_static_params_with_capture_all_args(
            self, arg_a, *args
        ) -> None:
            self.key_binding_result = (arg_a, args)

        def action_multiple_with_only_capture_all_args(self, *args) -> None:
            self.key_binding_result = args

        def action_dynamic_param(self, key: str):
            self.key_binding_result = f"key pressed: {key}"

        def action_dynamic_and_static_params(self, key: str, static: str):
            self.key_binding_result = (f"key pressed: {key}", static)

    app = MyApp(test_name="key_binding_expressions")

    async with app.in_running_state() as clock_mock:

        async def press_key(key: str) -> None:
            await app.press(Key(..., key))

        async def wait_for_key_processing() -> None:
            await clock_mock.advance_clock(0.001)

        assert app.key_binding_result is None

        # Simplest binding, no params:
        await press_key("h")
        await wait_for_key_processing()
        assert app.key_binding_result == "hello_world"

        # Binding with static params:
        await press_key("s")
        await wait_for_key_processing()
        assert app.key_binding_result == "this is a static param"

        # Binding with multiple static params:
        await press_key("m")
        await wait_for_key_processing()
        assert app.key_binding_result == ("correct horse", "battery staple")

        # Binding with multiple static params, with a "capture all" param:
        await press_key("c")
        await wait_for_key_processing()
        assert app.key_binding_result == (1, ("a", {0: 1e5}, True, [2, 3]))

        # Binding with multiple static params, with _only_ a "capture all" param:
        await press_key("a")
        await wait_for_key_processing()
        assert app.key_binding_result == (-1, 3.14, None)

        # Dynamic parameters binding:
        for i in range(3):
            await press_key(str(i))
            await wait_for_key_processing()
            assert app.key_binding_result == f"key pressed: {i}"

        # Dynamic and static parameters binding:
        for i in range(5, 7):
            await press_key(str(i))
            await wait_for_key_processing()
            assert app.key_binding_result == (
                f"key pressed: {i}",
                {"key": "static value"},
            )

        # Various more advanced dynamic parameters binding:
        for i in range(8, 10):
            await press_key(str(i))
            await wait_for_key_processing()
            assert app.key_binding_result == (
                (
                    "Ellipsis",
                    False,
                    "static",
                    str(i),
                    "textual.events",
                    "(<class 'textual.events.Key'>, <class 'textual.events.InputEvent'>, <class 'textual.events.Event'>, <class 'textual.message.Message'>, <class 'object'>)",
                )
            )
