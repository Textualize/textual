from textual.app import App

from textual.layout import Container
from textual.widgets import DirectoryTree


class TreeApp(App):
    def compose(self):
        tree = DirectoryTree("~/projects")
        yield Container(tree)
        tree.focus()


app = TreeApp()
if __name__ == "__main__":
    app.run()
