from textual.app import App, ComposeResult
from textual.widgets import Button, TabbedContent


class FiddleWithTabsApp(App[None]):
    CSS = """
    TabPane:disabled {
        background: red;
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent():
            yield Button()
            yield Button()
            yield Button()
            yield Button()
            yield Button()

    def on_mount(self) -> None:
        self.query_one(TabbedContent).disable_tab("tab-1")
        self.query_one(TabbedContent).disable_tab("tab-2")
        self.query_one(TabbedContent).hide_tab("tab-3")


if __name__ == "__main__":
    FiddleWithTabsApp().run()
