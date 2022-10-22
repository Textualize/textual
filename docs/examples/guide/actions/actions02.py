from textual.app import App
from textual import events


class ActionsApp(App):
    def action_set_background(self, color: str) -> None:
        self.screen.styles.background = color

    async def on_key(self, event: events.Key) -> None:
        if event.key == "r":
            await self.action("set_background('red')")


if __name__ == "__main__":
    app = ActionsApp()
    app.run()
