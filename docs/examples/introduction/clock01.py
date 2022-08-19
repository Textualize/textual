from datetime import datetime

from textual.app import App
from textual.widget import Widget


class Clock(Widget):
    def on_mount(self):
        self.styles.content_align = ("center", "middle")
        self.auto_refresh = 1.0

    def render(self):
        return datetime.now().strftime("%X")


class ClockApp(App):
    def compose(self):
        yield Clock()


app = ClockApp()
app.run()
