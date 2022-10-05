from textual.app import App, ComposeResult
from textual.color import Color
from textual.widgets import Static


class ColorApp(App):
    def compose(self) -> ComposeResult:
        self.widget1 = Static("Textual One")
        yield self.widget1
        self.widget2 = Static("Textual Two")
        yield self.widget2
        self.widget3 = Static("Textual Three")
        yield self.widget3

    def on_mount(self) -> None:
        self.widget1.styles.background = "#9932CC"
        self.widget2.styles.background = "hsl(150,42.9%,49.4%)"
        self.widget2.styles.color = "blue"
        self.widget3.styles.background = Color(191, 78, 96)


if __name__ == "__main__":
    app = ColorApp()
    app.run()
