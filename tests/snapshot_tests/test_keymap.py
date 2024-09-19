from __future__ import annotations
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.keymap import Keymap
from textual.widgets import Label


class KeymapApp(App[None]):
    BINDINGS = [
        Binding(key="i,up", action="increment", id="app.increment"),
    ]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.count = 0

    def compose(self) -> ComposeResult:
        yield Label("foo")

    def get_keymap(self) -> Keymap:
        return Keymap(
            {
                "app.increment": "right,k",
            }
        )

    def action_increment(self) -> None:
        self.count += 1


async def test_keymap_default_binding_replaces_old_binding():
    app = KeymapApp()
    async with app.run_test() as pilot:
        # The original bindings are removed - action not called.
        await pilot.press("i", "up")
        assert app.count == 0

        # The new bindings are active and call the action.
        await pilot.press("right", "k")
        assert app.count == 2
