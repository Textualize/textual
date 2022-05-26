from textual.app import App


class ExampleApp(App):

    COLORS = [
        "white",
        "maroon",
        "red",
        "purple",
        "fuchsia",
        "olive",
        "yellow",
        "navy",
        "teal",
        "aqua",
    ]

    def on_mount(self):
        self.styles.background = "darkblue"

    def on_key(self, event):
        if event.key.isdigit():
            self.styles.background = self.COLORS[int(event.key)]
        self.bell()


app = ExampleApp()
app.run()
