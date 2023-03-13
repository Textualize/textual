from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Label


class VerticalRemoveApp(App[None]):
    CSS = """
    Vertical {
        border: round green;
        height: auto;
    }

    Label {
        border: round yellow;
        background: red;
        color: yellow;
    }
    """
    BINDINGS = [
        ("a", "add", "Add"),
        ("d", "del", "Delete"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical()
        yield Footer()

    def action_add(self) -> None:
        self.query_one(Vertical).mount(Label("This is a test label"))

    def action_del(self) -> None:
        if self.query_one(Vertical).children:
            self.query_one(Vertical).children[-1].remove()


if __name__ == "__main__":
    VerticalRemoveApp().run()
