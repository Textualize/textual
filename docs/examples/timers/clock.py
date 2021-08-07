from datetime import datetime

from rich.align import Align

from textual.app import App
from textual.widget import Widget


class Clock(Widget):
    async def on_mount(self, event):
        self.set_interval(1, callback=self.refresh)

    def render(self) -> Align:
        time = datetime.now().strftime("%X")
        return Align.center(time, vertical="middle")

class ClockApp(App):
    async def on_mount(self, event):
        await self.view.dock(Clock())


ClockApp.run()
