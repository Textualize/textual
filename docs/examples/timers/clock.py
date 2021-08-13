from datetime import datetime

from rich.align import Align

from textual.app import App
from textual.widget import Widget


class Clock(Widget):
    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        time = datetime.now().strftime("%c")
        return Align.center(time, vertical="middle")


class ClockApp(App):
    async def on_mount(self):
        await self.view.dock(Clock())


ClockApp.run()
