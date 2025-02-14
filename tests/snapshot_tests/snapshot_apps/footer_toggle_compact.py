from textual.app import App, ComposeResult
from textual.widgets import Footer, Label


class ToggleCompactFooterApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    """

    BINDINGS = [
        ("ctrl+t", "toggle_compact_footer", "Toggle Compact Footer"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("Compact Footer")
        yield Footer()

    def on_mount(self) -> None:
        footer = self.query_one(Footer)
        footer.compact = True

    def action_toggle_compact_footer(self) -> None:
        footer = self.query_one(Footer)
        footer.compact = not footer.compact
        footer_type = "Compact" if footer.compact else "Standard"
        self.query_one(Label).update(f"{footer_type} Footer")


if __name__ == "__main__":
    app = ToggleCompactFooterApp()
    app.run()
