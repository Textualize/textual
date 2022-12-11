from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer


class ListViewExample(App):

    CSS_PATH = "list_view.css"

    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()


if __name__ == "__main__":
    app = ListViewExample()
    app.run()
