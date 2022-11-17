import json

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree


with open("food.json") as data_file:
    data = json.load(data_file)

from rich import print

print(data)


class TreeApp(App):

    BINDINGS = [("a", "add", "Add node")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Tree("Root")

    def action_add(self) -> None:
        tree = self.query_one(Tree)

        tree.add_json(data)


if __name__ == "__main__":
    app = TreeApp()
    app.run()
