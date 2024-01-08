from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane

class TabRenameApp(App[None]):

    def compose(self) -> ComposeResult:
        with TabbedContent():
            yield TabPane("!", id="test")
            for n in range(5):
                yield TabPane(str(n) * (n+1))

    def on_mount(self) -> None:
        self.query_one(TabbedContent).get_tab("test").label = "This is a much longer label for the tab"

if __name__ == "__main__":
    TabRenameApp().run()
