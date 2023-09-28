from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class MyWidget(Widget):
    SCOPED_CSS = False
    DEFAULT_CSS = """
    MyWidget {
        height: auto;
        border: magenta;
    }
    Label {
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("foo")
        yield Label("bar")

    def on_mount(self) -> None:
        self.log(self.app.stylesheet.css)


class MyApp(App):
    def compose(self) -> ComposeResult:
        yield MyWidget()
        yield MyWidget()
        yield Label("This will be styled")


if __name__ == "__main__":
    app = MyApp()
    app.run()
