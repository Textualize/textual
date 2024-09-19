from __future__ import annotations
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.keymap import Keymap
from textual.widgets import Label


class Counter(App[None]):
    BINDINGS = [
        Binding(key="i,up", action="increment", id="app.increment"),
        Binding(key="d,down", action="decrement", id="app.decrement"),
    ]

    def __init__(self, keymap: Keymap, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.count = 0
        self.keymap = keymap

    def compose(self) -> ComposeResult:
        yield Label("foo")

    def get_keymap(self) -> Keymap:
        return self.keymap

    def action_increment(self) -> None:
        self.count += 1


async def test_keymap_default_binding_replaces_old_binding():
    app = Counter(keymap=Keymap({"app.increment": "right,k"}))
    async with app.run_test() as pilot:
        # The original bindings are removed - action not called.
        await pilot.press("i", "up")
        assert app.count == 0

        # The new bindings are active and call the action.
        await pilot.press("right", "k")
        assert app.count == 2


async def test_keymap_binding_clashes_with_existing_binding():
    app = Counter(keymap=Keymap({"app.increment": "d"}))
    async with app.run_test() as pilot:
        # We've created a binding that clashes with the existing "decrement" binding.
        pass
        # TODO - test that the clashed binding is returned


# TODO - rebind a key to the same key... no crash?
# TODO - test that key_display is reset to None (and get_key_display is used) when a binding is overridden
# TODO - test that you can unbind a key and have a None binding without a crash
