from __future__ import annotations

from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, Keymap
from textual.events import BindingsClash
from textual.widgets import Label


class Counter(App[None]):
    BINDINGS = [
        Binding(key="i,up", action="increment", id="app.increment"),
        Binding(key="d,down", action="decrement", id="app.decrement"),
    ]

    def __init__(self, keymap: Keymap, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.count = 0
        self.bindings_clash = None
        self.keymap = keymap

    def compose(self) -> ComposeResult:
        yield Label("foo")

    def get_keymap(self) -> Keymap:
        return self.keymap

    def action_increment(self) -> None:
        self.count += 1

    def action_decrement(self) -> None:
        self.count -= 1

    @on(BindingsClash)
    def handle_bindings_clash(self, event: BindingsClash) -> None:
        self.bindings_clash = event


async def test_keymap_default_binding_replaces_old_binding():
    app = Counter(Keymap({"app.increment": "right,k"}))
    async with app.run_test() as pilot:
        # The original bindings are removed - action not called.
        await pilot.press("i", "up")
        assert app.count == 0

        # The new bindings are active and call the action.
        await pilot.press("right", "k")
        assert app.count == 2


async def test_keymap_sends_message_when_clash():
    app = Counter(Keymap({"app.increment": "d"}))
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert app.bindings_clash is not None
        assert app.bindings_clash.node == app
        assert len(app.bindings_clash.bindings) == 1
        clash = app.bindings_clash.bindings.pop()
        assert clash.key == "d"
        assert clash.action == "increment"
        assert clash.id == "app.increment"


async def test_keymap_with_unknown_id_is_noop():
    app = Counter(Keymap({"this.is.an.unknown.id": "d"}))
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert app.count == -1
