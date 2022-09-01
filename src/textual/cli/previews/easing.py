from textual._easing import EASING
from textual.app import ComposeResult, App
from textual.widget import Widget
from textual.widgets import Button, Static


class EasingButtons(Widget):
    def compose(self) -> ComposeResult:
        for easing in EASING:
            yield Button(easing)


class EasingApp(App):
    def compose(self) -> ComposeResult:
        yield EasingButtons()
        self.text = Static("Easing examples")
        yield self.text


app = EasingApp(css_path="easing.css", watch_css=True)
if __name__ == "__main__":
    app.run()
