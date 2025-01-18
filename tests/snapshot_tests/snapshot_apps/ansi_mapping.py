from textual.app import App, ComposeResult
from textual.widgets import Label


class AnsiMappingApp(App[None]):
    def compose(self) -> ComposeResult:
        ansi_colors = [
            "ansi_red",
            "ansi_green",
            "ansi_yellow",
            "ansi_blue",
            "ansi_magenta",
            "ansi_cyan",
            "ansi_white",
            "ansi_black",
        ]
        yield Label("Foreground & background")
        for color in ansi_colors:
            color_name = color.partition("_")[-1]
            yield Label(f"[{color}]{color_name}[/]")
            yield Label(f"[dim {color}]dim {color_name}[/]")


app = AnsiMappingApp()
if __name__ == "__main__":
    app.run()
