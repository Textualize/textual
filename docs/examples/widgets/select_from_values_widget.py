from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Select

LINES = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.""".splitlines()


class SelectApp(App):
    CSS_PATH = "select.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select.from_values(LINES)

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)


if __name__ == "__main__":
    app = SelectApp()
    app.run()
