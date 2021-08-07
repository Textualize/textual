from textual.app import App


class Quiter(App):
    async def on_load(self, event):
        await self.bind("q", "quit")


Quiter.run()
