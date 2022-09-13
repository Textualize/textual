from textual.app import App, ComposeResult
from textual.widgets import Footer, Static


class Focusable(Static, can_focus=True):
    DEFAULT_CSS = """
    Focusable {
        background: blue 20%;        
        height: 1fr;
        padding: 1;
    }
    Focusable:hover {
        outline: solid white;
    }
    Focusable:focus {
        background: red 20%;
    }

    """


class Focusable1(Focusable):

    BINDINGS = [
        ("a", "app.bell", "Ding"),
    ]

    def render(self) -> str:
        return repr(self)


class Focusable2(Focusable):
    CSS = ""
    BINDINGS = [
        ("b", "app.bell", "Beep"),
        ("f1", "app.quit", "QUIT"),
    ]

    def render(self) -> str:
        return repr(self)


class BindingApp(App):
    BINDINGS = [("f1", "app.bell", "Bell")]

    def compose(self) -> ComposeResult:
        yield Focusable1()
        yield Focusable2()
        yield Footer()


app = BindingApp()
if __name__ == "__main__":
    app.run()
