from rich.console import RenderableType
from rich.markdown import Markdown
from rich.text import Text

from textual.app import App, ComposeResult

from textual.containers import Container, Horizontal
from textual.reactive import reactive, watch
from textual.widgets import Header, Footer, Static, Button, Checkbox, TextLog


WELCOME_MD = """

## Textual Demo

Welcome to the Textual demo!

- 

"""


class Body(Container):
    pass


class Title(Static):
    pass


class DarkSwitch(Horizontal):
    def compose(self) -> ComposeResult:
        yield Checkbox(value=self.app.dark)
        yield Static("Dark mode", classes="label")

    def on_mount(self) -> None:
        watch(self.app, "dark", self.on_dark_change)

    def on_dark_change(self, dark: bool) -> None:
        self.query_one(Checkbox).value = dark

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.app.dark = event.value


class Welcome(Container):
    def compose(self) -> ComposeResult:
        yield Static(Markdown(WELCOME_MD))


class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Title("Textual Demo")
        yield Container()
        yield DarkSwitch()


class DemoApp(App):
    CSS_PATH = "demo.css"
    TITLE = "Textual Demo"
    BINDINGS = [
        ("s", "app.toggle_class('Sidebar', '-hidden')", "Sidebar"),
        ("d", "app.toggle_dark", "Toggle Dark mode"),
        ("n", "app.toggle_class('TextLog', '-hidden')", "Notes"),
    ]

    show_sidebar = reactive(False)

    def add_note(self, renderable: RenderableType) -> None:
        self.query_one(TextLog).write(renderable)

    def on_mount(self) -> None:
        self.add_note("[b]Textual Nodes")

    def compose(self) -> ComposeResult:
        yield Container(
            Sidebar(),
            Header(),
            TextLog(classes="-hidden", wrap=False, highlight=True, markup=True),
            Body(Welcome()),
        )
        yield Footer()

    def on_dark_switch_toggle(self) -> None:
        self.dark = not self.dark


app = DemoApp()
if __name__ == "__main__":
    app.run()
