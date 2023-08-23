from textual.app import App, ComposeResult
from textual.widgets import Button, TabbedContent


class FiddleWithTabsApp(App[None]):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            yield Button()
            yield Button()
            yield Button()
            yield Button()
            yield Button()

    def on_mount(self) -> None:
        self.query_one(TabbedContent).disable_tab(f"tab-1")
        self.query_one(TabbedContent).disable_tab(f"tab-2")
        self.query_one(TabbedContent).hide_tab(f"tab-3")


if __name__ == "__main__":
    FiddleWithTabsApp().run()
