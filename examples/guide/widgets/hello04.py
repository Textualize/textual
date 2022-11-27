from itertools import cycle

from textual.app import App, ComposeResult
from textual.widgets import Static


hellos = cycle(
    [
        "Hola",
        "Bonjour",
        "Guten tag",
        "Salve",
        "Nǐn hǎo",
        "Olá",
        "Asalaam alaikum",
        "Konnichiwa",
        "Anyoung haseyo",
        "Zdravstvuyte",
        "Hello",
    ]
)


class Hello(Static):
    """Display a greeting."""

    DEFAULT_CSS = """
    Hello {
        width: 40;
        height: 9;
        padding: 1 2;
        background: $panel;
        border: $secondary tall;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        self.next_word()

    def on_click(self) -> None:
        self.next_word()

    def next_word(self) -> None:
        """Get a new hello and update the content area."""
        hello = next(hellos)
        self.update(f"{hello}, [b]World[/b]!")


class CustomApp(App):
    CSS_PATH = "hello04.css"

    def compose(self) -> ComposeResult:
        yield Hello()


if __name__ == "__main__":
    app = CustomApp()
    app.run()
