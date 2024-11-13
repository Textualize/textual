from textual.app import App, ComposeResult
from textual.widgets import Label

COLORS = ("primary", "secondary", "accent", "warning", "error", "success")


class MutedBackgrounds(App[None]):
    CSS = "\n".join(
        f".text-{color} {{padding: 0 1; color: $text-{color}; background: ${color}-muted;}}"
        for color in COLORS
    )

    def compose(self) -> ComposeResult:
        for color in COLORS:
            yield Label(f"$text-{color} on ${color}-muted", classes=f"text-{color}")


app = MutedBackgrounds()
if __name__ == "__main__":
    app.run()
