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
        yield Label("[fg on bg]Foreground & background[/]")
        for color in ansi_colors:
            yield Label(f"[{color}]{color}[/]")
            yield Label(f"[dim {color}]dim {color}[/]")


app = AnsiMappingApp()
if __name__ == "__main__":
    app.run()
