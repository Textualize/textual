from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive, var
from textual.widgets import Label

GREETINGS = [
    "Bonjour",
    "Hola",
    "こんにちは",
    "你好",
    "안녕하세요",
    "Hello",
]


class Greeter(Horizontal):
    """Display a greeting and a name."""

    DEFAULT_CSS = """
    Greeter {
        width: auto;
        height: 1;
        & Label {
            margin: 0 1;
        }
    }
    """
    greeting: reactive[str] = reactive("")
    who: reactive[str] = reactive("")

    def __init__(self, greeting: str = "Hello", who: str = "World!") -> None:
        super().__init__()
        self.greeting = greeting  # (1)!
        self.who = who

    def compose(self) -> ComposeResult:
        yield Label(self.greeting, id="greeting")
        yield Label(self.who, id="name")

    def watch_greeting(self, greeting: str) -> None:
        self.query_one("#greeting", Label).update(greeting)  # (2)!

    def watch_who(self, who: str) -> None:
        self.query_one("#who", Label).update(who)


class NameApp(App):

    CSS = """
    Screen {
        align: center middle;
    }   
    """
    greeting_no: var[int] = var(0)
    BINDINGS = [("space", "greeting")]

    def compose(self) -> ComposeResult:
        yield Greeter(who="Textual")

    def action_greeting(self) -> None:
        self.greeting_no = (self.greeting_no + 1) % len(GREETINGS)
        self.query_one(Greeter).greeting = GREETINGS[self.greeting_no]


if __name__ == "__main__":
    app = NameApp()
    app.run()
