from __future__ import annotations

import inspect

from rich.syntax import Syntax

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen, Screen
from textual.widgets import Static


class CodeScreen(ModalScreen):
    DEFAULT_CSS = """
    CodeScreen {
        #code {
            border: heavy $accent;
            margin: 2 4;
            scrollbar-gutter: stable;
            Static {
                width: auto;
            }
        }
    }
    """
    BINDINGS = [("escape", "dismiss", "Dismiss code")]

    def __init__(self, title: str, code: str) -> None:
        super().__init__()
        self.code = code
        self.title = title

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="code"):
            yield Static(
                Syntax(
                    self.code, lexer="python", indent_guides=True, line_numbers=True
                ),
                expand=True,
            )

    def on_mount(self):
        code_widget = self.query_one("#code")
        code_widget.border_title = self.title
        code_widget.border_subtitle = "Escape to close"


class PageScreen(Screen):
    DEFAULT_CSS = """
    PageScreen {
        width: 100%;
        height: 1fr;
        overflow-y: auto;        
    }
    """
    BINDINGS = [
        Binding(
            "c",
            "show_code",
            "Code",
            tooltip="Show the code used to generate this screen",
        )
    ]

    @work(thread=True)
    def get_code(self, source_file: str) -> str | None:
        """Read code from disk, or return `None` on error."""
        try:
            with open(source_file, "rt", encoding="utf-8") as file_:
                return file_.read()
        except Exception:
            return None

    async def action_show_code(self):
        source_file = inspect.getsourcefile(self.__class__)
        if source_file is None:
            self.notify(
                "Could not get the code for this page",
                title="Show code",
                severity="error",
            )
            return

        code = await self.get_code(source_file).wait()
        if code is None:
            self.notify(
                "Could not get the code for this page",
                title="Show code",
                severity="error",
            )
        else:
            self.app.push_screen(CodeScreen("Code for this page", code))
