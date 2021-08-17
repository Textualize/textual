from textual.app import App


class ColorChanger(App):
    def on_key(self, event):
        if event.key.isdigit():
            self.background = f"on color({event.key})"


ColorChanger.run(log="textual.log")
