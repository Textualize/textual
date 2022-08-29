from textual.app import App

from textual.widgets import Static


class TableLayoutApp(App):
    def compose(self):
        yield Static("foo", id="foo")
        yield Static("bar")
        yield Static("baz")

        yield Static("foo")
        yield Static("bar")
        yield Static("baz", id="last")


app = TableLayoutApp(css_path="table_layout.css")
if __name__ == "__main__":
    app.run()
