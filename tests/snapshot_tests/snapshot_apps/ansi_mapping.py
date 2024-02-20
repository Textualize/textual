from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Label


class AnsiMappingApp(App[None]):
    def compose(self) -> ComposeResult:
        ansi_colors = [
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "black",
        ]
        yield Label("[default on default]Default foreground & background[/]")
        for color in ansi_colors:
            yield Label(f"[{color}]Hello, {color}![/]")
            yield Label(f"[dim {color}]Hello, dim {color}![/]")


app = AnsiMappingApp()
if __name__ == "__main__":
    app.run()
