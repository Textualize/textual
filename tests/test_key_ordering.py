"""Regression tests for https://github.com/Textualize/textual/issues/6605

Keys handled by bindings (such as backspace) used to take a detour through
ancestor message queues before their action ran, so under fast input they
could be applied out of order with printable keys, which Input and TextArea
handle directly.
"""

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea


def type_fast(app: App, *keys: str) -> None:
    """Post key events back to back, without waiting for each to settle."""
    for key in keys:
        app.post_message(events.Key(key, key if len(key) == 1 else None))


async def test_input_binding_keys_apply_in_order_with_typed_text():
    class KeysApp(App):
        def compose(self) -> ComposeResult:
            yield Input()

    app = KeysApp()
    async with app.run_test() as pilot:
        type_fast(app, "b", "a", "backspace", "c")
        for _ in range(3):
            await pilot.pause()
        assert app.query_one(Input).value == "bc"


async def test_text_area_binding_keys_apply_in_order_with_typed_text():
    class KeysApp(App):
        def compose(self) -> ComposeResult:
            yield TextArea()

    app = KeysApp()
    async with app.run_test() as pilot:
        type_fast(app, "b", "a", "backspace", "c")
        for _ in range(3):
            await pilot.pause()
        assert app.query_one(TextArea).text == "bc"
