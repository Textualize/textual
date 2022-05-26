from unittest import mock

import pytest

from tests.utilities.test_app import AppTest
from textual import actions
from textual.events import Key


@pytest.mark.asyncio
async def test_valid_key_binding_expressions():
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
                "d": "multiple_static_params('Huey', 'Dewey', 'Louie - should not be passed')",
                "c": "multiple_static_params_with_capture_all_args(1, 'a', {0: 1e5}, True, [2, 3])",
                "a": "multiple_with_only_capture_all_args(-1, 3.14, None)",
                "0": "dynamic_param_is_object('$event')",
                "2,3": "dynamic_param('$event.key')",
                "5,6": "dynamic_and_static_params('$event.key', {'key': 'static value'}, '$event.verbosity')",
                "8,9": """multiple_with_only_capture_all_args("$event.sender", "$event.is_forwarded", "static", "$event.key", 3)""",
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

        def action_dynamic_param_is_object(self, object: object):
            self.key_binding_result = object

        def action_dynamic_and_static_params(
            self, key: str, static: str, event_verbosity: int
        ):
            self.key_binding_result = (f"key pressed: {key}", static, event_verbosity)

    app = MyApp(test_name="valid_key_binding_expressions")

    async with app.in_running_state() as clock_mock:

        async def press_key(key: str) -> None:
            await app.press(key)

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

        # Binding with multiple static params, the event handler accept less than we pass:
        await press_key("d")
        await wait_for_key_processing()
        # The 3rd param should not be passed - sorry Louie!
        assert app.key_binding_result == ("Huey", "Dewey")

        # Binding with multiple static params, with a "capture all" param:
        await press_key("c")
        await wait_for_key_processing()
        assert app.key_binding_result == (1, ("a", {0: 1e5}, True, [2, 3]))

        # Binding with multiple static params, with _only_ a "capture all" param:
        await press_key("a")
        await wait_for_key_processing()
        assert app.key_binding_result == (-1, 3.14, None)

        # Binding with dynamic event object param:
        await press_key("0")
        await wait_for_key_processing()
        assert (
            isinstance(app.key_binding_result, Key)
            and app.key_binding_result.key == "0"
        )

        # Dynamic parameters binding:
        for i in range(2, 4):
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
                1,  # event verbosity
            )

        # Various more advanced dynamic parameters binding:
        for i in range(8, 10):
            await press_key(str(i))
            await wait_for_key_processing()
            expected = (app, False, "static", str(i), 3)
            assert app.key_binding_result == expected


@pytest.mark.asyncio
async def test_invalid_key_binding_expressions():
    # ditto: would have been elegant if parametrised

    class MyApp(AppTest):
        def on_mount(self) -> None:
            bindings = {
                "a": "should_not_be_triggered('$unknown')",
                # We mock `__allowed_attributes_for_actions__` so the Key event class no longer
                # allow access to itself via the key "Self", so this should fail:
                "b": "should_not_be_triggered('$event')",
                "c": "should_not_be_triggered('$event._forwarded')",
                "d": "should_not_be_triggered('$event.__class__')",
                "e": "should_not_be_triggered('$event.key.lower')",
                "f": "should_not_be_triggered($syntax_error')",
            }
            for key, action in bindings.items():
                self.bind(key, action)

        def action_should_not_be_triggered(self) -> None:
            raise RuntimeError

    app = MyApp(test_name="invalid_key_binding_expressions")

    async with app.in_running_state() as clock_mock:

        async def press_key(key: str) -> None:
            await app.press(key)

        async def wait_for_key_processing() -> None:
            await clock_mock.advance_clock(0.001)

        with mock.patch(
            "textual.events.Key.__allowed_attributes_for_actions__", new=["key"]
        ):
            # Simplest binding, no params:
            for key, expected_error in [
                ("a", actions.NotAllowedActionExpression),
                ("b", actions.NotAllowedAttributeAccessInActionExpression),
                ("c", actions.NotAllowedAttributeAccessInActionExpression),
                ("d", actions.NotAllowedAttributeAccessInActionExpression),
                ("e", actions.TooManyLevelsInActionExpression),
                ("f", actions.ActionError),
            ]:
                with pytest.raises(expected_error):
                    await press_key(key)
                    await wait_for_key_processing()
