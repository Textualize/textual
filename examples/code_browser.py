import sys

from rich.syntax import Syntax
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.layout import Container, Vertical
from textual.reactive import Reactive
from textual.widgets import DirectoryTree, Footer, Header, Static


class CodeBrowser(App):

    show_tree = Reactive.init(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        self.set_class(show_tree, "-show-tree")

    def on_load(self) -> None:
        self.bind("t", "toggle_tree", description="Toggle Tree")
        self.bind("q", "quit", description="Quit")

    def compose(self) -> ComposeResult:
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        yield Container(
            Vertical(DirectoryTree(path), id="tree-view"),
            Vertical(Static(id="code"), id="code-view"),
        )
        yield Footer()

    def on_directory_tree_file_click(self, event: DirectoryTree.FileClick) -> None:
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(event.path, line_numbers=True, word_wrap=True)
        except Exception:
            code_view.update(Traceback())
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = event.path

    def action_toggle_tree(self) -> None:
        self.show_tree = not self.show_tree


app = CodeBrowser(css_path="code_browser.css")
if __name__ == "__main__":
    app.run()
