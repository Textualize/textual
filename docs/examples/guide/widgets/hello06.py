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

    BORDER_TITLE = "Hello Widget"  # (1)!

    def on_mount(self) -> None:
        self.action_next_word()
        self.border_subtitle = "Click for next hello"  # (2)!

    def action_next_word(self) -> None:
        """Get a new hello and update the content area."""
        hello = next(hellos)
        self.update(f"[@click='next_word']{hello}[/], [b]World[/b]!")


class CustomApp(App):
    CSS_PATH = "hello05.tcss"

    def compose(self) -> ComposeResult:
        yield Hello()


if __name__ == "__main__":
    app = CustomApp()
    app.run()
