from __future__ import annotations

from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding, Keymap
from textual.dom import DOMNode
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
        self.clashed_bindings: set[Binding] | None = None
        self.clashed_node: DOMNode | None = None
        self.keymap = keymap

    def compose(self) -> ComposeResult:
        yield Label("foo")

    def on_mount(self) -> None:
        self.set_keymap(self.keymap)

    def action_increment(self) -> None:
        self.count += 1

    def action_decrement(self) -> None:
        self.count -= 1

    def handle_bindings_clash(
        self, clashed_bindings: set[Binding], node: DOMNode
    ) -> None:
        self.clashed_bindings = clashed_bindings
        self.clashed_node = node


async def test_keymap_default_binding_replaces_old_binding():
    app = Counter({"app.increment": "right,k"})
    async with app.run_test() as pilot:
        # The original bindings are removed - action not called.
        await pilot.press("i", "up")
        assert app.count == 0

        # The new bindings are active and call the action.
        await pilot.press("right", "k")
        assert app.count == 2


async def test_keymap_sends_message_when_clash():
    app = Counter({"app.increment": "d"})
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert app.clashed_bindings is not None
        assert len(app.clashed_bindings) == 1
        clash = app.clashed_bindings.pop()
        assert app.clashed_node is app
        assert clash.key == "d"
        assert clash.action == "increment"
        assert clash.id == "app.increment"


async def test_keymap_with_unknown_id_is_noop():
    app = Counter({"this.is.an.unknown.id": "d"})
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert app.count == -1


async def test_keymap_inherited_bindings_same_id():
    """When a child widget inherits from a parent widget, if they have
    a binding with the same ID, then both parent and child bindings will
    be overridden by the keymap (assuming the keymap has a mapping with the
    same ID)."""

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

        def on_mount(self) -> None:
            self.set_keymap({"increment": "i"})

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


async def test_keymap_child_with_different_id_overridden():
    """Ensures that overriding a parent binding doesn't influence a child
    binding with a different ID."""

    parent_counter = 0
    child_counter = 0

    class Parent(Widget, can_focus=True):
        BINDINGS = [
            Binding(key="x", action="increment", id="parent.increment"),
        ]

        def action_increment(self) -> None:
            nonlocal parent_counter
            parent_counter += 1

    class Child(Parent):
        BINDINGS = [
            Binding(key="x", action="increment", id="child.increment"),
        ]

        def action_increment(self) -> None:
            nonlocal child_counter
            child_counter += 1

    class MyApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Parent()
            yield Child()

        def on_mount(self) -> None:
            self.set_keymap({"parent.increment": "i"})

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

        # Default binding is still active on the child.
        await pilot.press("x")
        assert parent_counter == 1
        assert child_counter == 1

        # The binding from the keymap only affects the parent, so
        # pressing it with the child focused does nothing.
        await pilot.press("i")
        assert parent_counter == 1
        assert child_counter == 1


async def test_set_keymap_before_app_mount():
    """Ensure we can set the keymap before mount without crash.

    https://github.com/Textualize/textual/issues/5742
    """

    worked = False

    class MyApp(App[None]):

        BINDINGS = [Binding(key="x", action="test", id="test")]

        def __init__(self) -> None:
            super().__init__()
            self.update_keymap({"test": "y"})

        def action_test(self) -> None:
            nonlocal worked
            worked = True

    async with MyApp().run_test() as pilot:
        await pilot.press("y")
        assert worked is True
