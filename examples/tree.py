import json

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree


with open("food.json") as data_file:
    data = json.load(data_file)

from rich import print

print(data)


class TreeApp(App):

    BINDINGS = [
        ("a", "add", "Add node"),
        ("c", "clear", "Clear"),
        ("t", "toggle_root", "Toggle root"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Tree("Root")

    def action_add(self) -> None:
        tree = self.query_one(Tree)

        json_node = tree.root.add("JSON")
        tree.root.expand()
        tree.add_json(json_node, data)

    def action_clear(self) -> None:
        tree = self.query_one(Tree)
        tree.clear()

    def action_toggle_root(self) -> None:
        tree = self.query_one(Tree)
        tree.show_root = not tree.show_root


if __name__ == "__main__":
    app = TreeApp()
    app.run()
