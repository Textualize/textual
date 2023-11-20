from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Select

LINES = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.""".splitlines()

ALTERNATE_LINES = """Twinkle, twinkle, little star,
How I wonder what you are!
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are!""".splitlines()


class SelectApp(App):
    CSS_PATH = "select.tcss"

    BINDINGS = [("s", "swap", "Swap Select options")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select(zip(LINES, LINES), allow_blank=False)

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)

    def action_swap(self) -> None:
        self.query_one(Select).set_options(zip(ALTERNATE_LINES, ALTERNATE_LINES))


if __name__ == "__main__":
    app = SelectApp()
    app.run()
