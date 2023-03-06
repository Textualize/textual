from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox


class CheckboxApp(App[None]):
    CSS_PATH = "checkbox.css"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Checkbox("Arrakis :sweat:")
            yield Checkbox("Caladan")
            yield Checkbox("Chusuk")
            yield Checkbox("[b]Giedi Prime[/b]")
            yield Checkbox("[magenta]Ginaz[/]")
            yield Checkbox("Grumman", True)
            yield Checkbox("Kaitain", id="initial_focus")
            yield Checkbox("Novebruns", True)

    def on_mount(self):
        self.query_one("#initial_focus", Checkbox).focus()


if __name__ == "__main__":
    CheckboxApp().run()
