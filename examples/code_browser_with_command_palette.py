"""
Code browser example.

Run with:

    python code_browser.py PATH
"""

import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import AsyncIterator

from rich.align import Align
from rich.columns import Columns
from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import Traceback

from textual.app import App, ComposeResult
from textual.command_palette import (
    CommandMatches,
    CommandPalette,
    CommandSource,
    CommandSourceHit,
)
from textual.containers import Container, VerticalScroll
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, Static


class FileNameSource(CommandSource):
    """A source of filename-based commands for the CommandPalette."""

    @classmethod
    async def _iter_dir(cls, path: Path) -> AsyncIterator[Path]:
        for child in path.iterdir():
            if child.is_file():
                yield child
            elif child.is_dir() and not child.name.startswith("."):
                async for sub_child in cls._iter_dir(child):
                    yield sub_child

    async def hunt_for(self, user_input: str) -> CommandMatches:
        assert isinstance(self.app, CodeBrowser)
        matcher = self.matcher(user_input)
        async for candidate in self._iter_dir(
            Path(self.screen.query_one(DirectoryTree).path)
        ):
            if candidate.is_file():
                candidate_text = str(candidate)
                matched = matcher.match(candidate_text)
                if matched:
                    yield CommandSourceHit(
                        matched,
                        Columns(
                            [
                                Text.assemble(
                                    Text.from_markup("📄 [dim][i]open[/][/] "),
                                    matcher.highlight(candidate_text),
                                ),
                                Align.right(
                                    "[dim][i]"
                                    f"{candidate.stat().st_size} "
                                    f"{datetime.fromtimestamp(candidate.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
                                    "[/][/]"
                                ),
                            ],
                            expand=True,
                        ),
                        partial(self.app._view, Path(candidate)),
                        candidate_text,
                    )


class CodeBrowser(App):
    """Textual code browser app."""

    CSS_PATH = "code_browser.css"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        CommandPalette.register_source(FileNameSource)
        self.query_one(DirectoryTree).focus()

    def _view(self, code_file: Path) -> None:
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                str(code_file),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = str(code_file)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        self._view(event.path)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    CodeBrowser().run()
