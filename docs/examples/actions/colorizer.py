from textual.app import App


class Colorizer(App):
    async def on_load(self):
        await self.bind("r", "color('red')")
        await self.bind("g", "color('green')")
        await self.bind("b", "color('blue')")

    def action_color(self, color: str) -> None:
        self.background = f"on {color}"


Colorizer.run()
