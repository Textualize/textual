from textual.app import App
from textual.widget import Widget


class AlignApp(App):
    def on_load(self):
        self.bind("t", "log_tree")

    def on_mount(self) -> None:
        self.log("MOUNTED")
        self.mount(thing=Widget(), thing2=Widget())

    def action_log_tree(self):
        self.log(self.screen.tree)


AlignApp.run(css_file="align.css", log="textual.log", watch_css=True)
