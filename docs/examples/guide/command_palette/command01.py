from __future__ import annotations

from functools import partial
from pathlib import Path

from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.containers import VerticalScroll
from textual.widgets import Static


class PythonFileCommands(Provider):
    """A command provider to open a Python file in the current working directory."""

    def read_files(self) -> list[Path]:
        """Get a list of Python files in the current working directory."""
        return list(Path("./").glob("*.py"))

    async def startup(self) -> None:  # (1)!
        """Called once when the command palette is opened, prior to searching."""
        worker = self.app.run_worker(self.read_files, thread=True)
        self.python_paths = await worker.wait()

    async def search(self, query: str) -> Hits:  # (2)!
        """Search for Python files."""
        matcher = self.matcher(query)  # (3)!

        app = self.app
        assert isinstance(app, ViewerApp)

        for path in self.python_paths:
            command = f"open {str(path)}"
            score = matcher.match(command)  # (4)!
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),  # (5)!
                    partial(app.open_file, path),
                    help="Open this file in the viewer",
                )


class ViewerApp(App):
    """Demonstrate a command source."""

    COMMANDS = App.COMMANDS | {PythonFileCommands}  # (6)!

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static(id="code", expand=True)

    def open_file(self, path: Path) -> None:
        """Open and display a file with syntax highlighting."""
        from rich.syntax import Syntax

        syntax = Syntax.from_path(
            str(path),
            line_numbers=True,
            word_wrap=False,
            indent_guides=True,
            theme="github-dark",
        )
        self.query_one("#code", Static).update(syntax)


if __name__ == "__main__":
    app = ViewerApp()
    app.run()
