from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer


class ListViewExample(App):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()


app = ListViewExample(css_path="list_view.css")
if __name__ == "__main__":
    app.run()
