from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox


class CheckboxApp(App[None]):
    CSS_PATH = "checkbox.css"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Checkbox("Arrakis :sweat:"),
            Checkbox("Caladan"),
            Checkbox("Chusuk"),
            Checkbox("[b]Giedi Prime[/b]"),
            Checkbox("[magenta]Ginaz[/]"),
            Checkbox("Grumman", True),
            Checkbox("Kaitain", id="initial_focus"),
            Checkbox("Novebruns", True),
        )

    def on_mount(self):
        self.query_one("#initial_focus", Checkbox).focus()


if __name__ == "__main__":
    CheckboxApp().run()
