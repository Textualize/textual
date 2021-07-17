from textual.app import App


class ColorChanger(App):
    async def on_key(self, event):
        if event.key.isdigit():
            self.background = f"on color({event.key})"


ColorChanger.run()
