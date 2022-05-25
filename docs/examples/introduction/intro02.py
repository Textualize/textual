from textual.app import App


class ExampleApp(App):

    CSS = """

    """

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
        self.bind("t", "tree")

    def on_key(self, event):
        if event.key.isdigit():
            self.styles.background = self.COLORS[int(event.key)]
        self.bell()

    def action_tree(self):
        self.log(self.tree)

app = ExampleApp()
app.run()
