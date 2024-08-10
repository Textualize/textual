from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Footer, Switch
from textual.binding import Binding


class MyWidget(Widget, can_focus=True):
    BINDINGS = [
        Binding("space", "app.bell", "Bell (Widget)"),
        Binding("a", "app.notify('a widget')", "widget"),
        Binding("b", "app.notify('b widget')", "widget"),
    ]

    DEFAULT_CSS = """
    MyWidget {
        border: solid green;
        height: 5;
    }
    """


class BindApp(App):
    BINDINGS = [
        Binding("space", "app.bell", "Bell (App)"),
        Binding("c", "app.notify('c app')", "app"),
        Binding("a", "app.notify('a app')", "app"),
        Binding("b", "app.notify('b app')", "app"),
    ]

    def compose(self) -> ComposeResult:
        yield MyWidget()
        yield Switch()
        yield Footer()

    def action_notify(self, msg: str):
        self.notify(msg)


if __name__ == "__main__":
    app = BindApp()
    app.run()
