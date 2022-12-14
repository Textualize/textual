from textual.app import App, ComposeResult
from textual.widgets import Static


class BackgroundTransparencyApp(App):
    """Simple app to exemplify different transparency settings."""
    def compose(self) -> ComposeResult:
        yield Static("10%", id="t10")
        yield Static("20%", id="t20")
        yield Static("30%", id="t30")
        yield Static("40%", id="t40")
        yield Static("50%", id="t50")
        yield Static("60%", id="t60")
        yield Static("70%", id="t70")
        yield Static("80%", id="t80")
        yield Static("90%", id="t90")
        yield Static("100%", id="t100")


app = BackgroundTransparencyApp(css_path="background_transparency.css")
