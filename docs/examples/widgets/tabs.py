from textual.app import App, ComposeResult
from textual.widgets import Label, Tabs


class TabsApp(App):
    CSS = """
    Tabs {
        dock: top;
    }
    Screen {
        align: center middle;
    }
    Label {
        margin:1 1;
        width: 100%;
        height: 100%;
        background: $panel;
        border: tall $primary;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Tabs(
            "Paul Atreidies",
            "Duke Leto Atreides",
            "Lady Jessica",
            "Gurney Halleck",
            "Baron Vladimir Harkonnen",
            "Glossu Rabban",
            "Chani",
            "Silgar",
        )
        yield Label()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.query_one(Label).update(event.tab.label)


if __name__ == "__main__":
    app = TabsApp()
    app.run()
