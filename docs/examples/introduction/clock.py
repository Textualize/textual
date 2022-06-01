from datetime import datetime

from textual.app import App
from textual.widget import Widget


class Clock(Widget):
    def on_mount(self):
        self.styles.content_align = ("center", "middle")
        self.set_interval(1, self.refresh)

    def render(self):
        return datetime.now().strftime("%c")


class ClockApp(App):
    def compose(self):
        yield Clock()
