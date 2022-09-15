from textual.app import App, ComposeResult
from textual.widgets import Static


class WidgetApp(App):
    def compose(self) -> ComposeResult:
        self.widget = Static("Textual")
        yield self.widget

    def on_mount(self) -> None:
        self.widget.styles.background = "darkblue"
        self.widget.styles.border = ("heavy", "white")


app = WidgetApp()
if __name__ == "__main__":
    app.run()
