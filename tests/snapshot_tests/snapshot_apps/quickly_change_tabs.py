"""Regression test for https://github.com/Textualize/textual/issues/2229."""
from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Tabs, DirectoryTree


class QuicklyChangeTabsApp(App[None]):
    CSS = """
    DirectoryTree {
        min-height: 10;
    }"""

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("one"):
                yield DirectoryTree("./")
            with TabPane("two"):
                yield DirectoryTree("./")
            with TabPane("three", id="three"):
                yield DirectoryTree("./")

    def key_p(self) -> None:
        self.query_one(Tabs).action_next_tab()
        self.query_one(Tabs).action_next_tab()


app = QuicklyChangeTabsApp()

if __name__ == "__main__":
    app.run()
