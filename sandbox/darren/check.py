from textual.app import App, ComposeResult

from textual.containers import Container
from textual.widgets import Checkbox, Footer


class CheckboxApp(App):
    BINDINGS = [("s", "switch", "Press switch"), ("d", "toggle_dark", "Dark mode")]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Container(Checkbox(id="check", animate=True))

    def action_switch(self) -> None:
        checkbox = self.query_one(Checkbox)
        checkbox.toggle()

    def key_f(self):
        print(self.app.focused)


app = CheckboxApp(css_path="check.css")
if __name__ == "__main__":
    app.run()
