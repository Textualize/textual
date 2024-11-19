from textual.app import App, ComposeResult
from textual.widgets import Label

COLORS = ("primary", "secondary", "accent", "warning", "error", "success")


class ColoredText(App[None]):
    CSS = "\n".join(f".text-{color} {{color: $text-{color};}}" for color in COLORS)

    def compose(self) -> ComposeResult:
        for color in COLORS:
            yield Label(f"$text-{color}", classes=f"text-{color}")


app = ColoredText()
if __name__ == "__main__":
    app.run()
