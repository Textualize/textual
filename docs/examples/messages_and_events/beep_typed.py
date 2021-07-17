from textual.app import App
from textual import events


class Beeper(App):
    async def on_key(self, event: events.Key) -> None:
        self.console.bell()


Beeper.run()
