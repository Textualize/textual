from __future__ import annotations

from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, Keymap
from textual.events import BindingsClash
from textual.widget import Widget
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


async def test_keymap_inherited_bindings_same_id():
    parent_counter = 0
    child_counter = 0

    class Parent(Widget, can_focus=True):
        BINDINGS = [
            Binding(key="x", action="increment", id="increment"),
        ]

        def action_increment(self) -> None:
            nonlocal parent_counter
            parent_counter += 1

    class Child(Parent):
        BINDINGS = [
            Binding(key="x", action="increment", id="increment"),
        ]

        def action_increment(self) -> None:
            nonlocal child_counter
            child_counter += 1

    class MyApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Parent()
            yield Child()

        def get_keymap(self) -> Keymap:
            return Keymap({"increment": "i"})

    app = MyApp()
    async with app.run_test() as pilot:
        # Default binding is unbound due to keymap.
        await pilot.press("x")
        assert parent_counter == 0
        assert child_counter == 0

        # New binding is active, parent is focused - action called.
        await pilot.press("i")
        assert parent_counter == 1
        assert child_counter == 0

        # Tab to focus the child.
        await pilot.press("tab")

        # Default binding results in no change.
        await pilot.press("x")
        assert parent_counter == 1
        assert child_counter == 0

        # New binding is active, child is focused - action called.
        await pilot.press("i")
        assert parent_counter == 1
        assert child_counter == 1
