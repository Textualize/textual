from textual.app import App
from textual.layout import Container
from textual.widgets import Header, Footer, Static


class Content(Static):
    pass


class Panel(Container):
    pass


class Panel2(Container):
    pass


class DesignApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self):
        yield Header()
        yield Footer()
        yield Panel(
            Content("content"),
            Panel(
                Content("more content"),
                Content("more content"),
            ),
        )
        yield Panel(Static("Hello World"))


app = DesignApp(css_path="design.css")
if __name__ == "__main__":
    app.run()
