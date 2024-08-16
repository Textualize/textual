from __future__ import annotations

from typing import TYPE_CHECKING

from .screen import Screen

if TYPE_CHECKING:
    from .app import ComposeResult


class SystemScreen(Screen):
    DEFAULT_CSS = """
    SystemScreen {
        Label {
            height: 3;
            color: red;
            split: right;
        }

    }
    """

    def compose(self) -> ComposeResult:
        from .widgets import KeyPanel

        yield KeyPanel()
        # from .widgets import Label

        # yield Label("Hello World ! 12345\n" * 200)
