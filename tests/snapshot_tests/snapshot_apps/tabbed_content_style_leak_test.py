from textual.app import App, ComposeResult
from textual.widgets import Button, Label, TabbedContent, Tabs, TabPane

class TabbedContentStyleLeakTestApp(App[None]):

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Leak Test"):
                yield Label("This label should come first")
                yield Button("This button should come second")
                yield Tabs("These", "Tabs", "Should", "Come", "Last")

if __name__ == "__main__":
    TabbedContentStyleLeakTestApp().run()
