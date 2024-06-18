from textual.app import App, ComposeResult
from textual.widgets import Footer


class CompactFooterApp(App):
    BINDINGS = [
        ("ctrl+t", "app.toggle_dark", "Toggle Dark mode"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_mount(self) -> None:
        footer = self.query_one(Footer)
        footer.compact = True


if __name__ == "__main__":
    app = CompactFooterApp()
    app.run()
