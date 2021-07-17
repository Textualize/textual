from textual.app import App


class Beeper(App):
    async def on_key(self, event):
        self.console.bell()


Beeper.run()
