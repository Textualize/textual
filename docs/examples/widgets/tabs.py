from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Tabs

NAMES = [
    "Paul Atreidies",
    "Duke Leto Atreides",
    "Lady Jessica",
    "Gurney Halleck",
    "Baron Vladimir Harkonnen",
    "Glossu Rabban",
    "Chani",
    "Silgar",
]


class TabsApp(App):
    """Demonstrates the Tabs widget."""

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

    BINDINGS = [
        ("a", "add", "Add tab"),
        ("r", "remove", "Remove active tab"),
        ("c", "clear", "Clear tabs"),
    ]

    def compose(self) -> ComposeResult:
        yield Tabs(NAMES[0])
        yield Label()
        yield Footer()

    def on_mount(self) -> None:
        """Focus the tabs when the app starts."""
        self.query_one(Tabs).focus()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        label = self.query_one(Label)
        if event.tab is None:
            # When the tabs are cleared, event.tab will be None
            label.visible = False
        else:
            label.visible = True
            label.update(event.tab.label)

    def action_add(self) -> None:
        """Add a new tab."""
        tabs = self.query_one(Tabs)
        # Cycle the names
        NAMES[:] = [*NAMES[1:], NAMES[0]]
        tabs.add_tab(NAMES[0])

    def action_remove(self) -> None:
        """Remove active tab."""
        tabs = self.query_one(Tabs)
        active_tab = tabs.active_tab
        if active_tab is not None:
            tabs.remove_tab(active_tab.id)

    def action_clear(self) -> None:
        """Clear the tabs."""
        self.query_one(Tabs).clear()


if __name__ == "__main__":
    app = TabsApp()
    app.run()
