from rich.console import RenderableType
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text

from textual.app import App, ComposeResult

from textual.containers import Container, Horizontal
from textual.reactive import reactive, watch
from textual.widgets import Header, Footer, Static, Button, Checkbox, TextLog


WELCOME_MD = """

## Textual Demo

Textual is a framework for creating sophisticated applications with the terminal.

Powered by **Rich**

GITHUB: https://github.com/Textualize/textual

"""

CSS_MD = """

Textual uses Cascading Stylesheets (CSS) to create Rich interactive User Interfaces.

- **Easy to learn** - much simpler than browser CSS
- **Live editing** - see your changes without restarting the app!

Here's an example of some CSS used in this app:

"""

EXAMPLE_CSS = """\
Screen {
    layers: base overlay notes;
    overflow: hidden;  
}

Sidebar {    
    width: 40;
    background: $panel;   
    transition: offset 500ms in_out_cubic;    
    layer: overlay;
    
}

Sidebar.-hidden {
    offset-x: -100%;
}"""


class Body(Container):
    pass


class Title(Static):
    def action_open_docs(self) -> None:
        self.app.bell()
        import webbrowser

        webbrowser.open("https://textual.textualize.io")


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
        yield Button("Start", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.add_note("[b magenta]Start!")
        self.app.query_one(".location-first").scroll_visible(speed=50)


class OptionGroup(Container):
    pass


class SectionTitle(Static):
    pass


class Option(Static):
    def __init__(self, label: str, reveal: str) -> None:
        super().__init__(label)
        self.reveal = reveal

    def on_click(self) -> None:
        self.app.query_one(self.reveal).scroll_visible()
        self.app.add_note(f"Scrolling to [b]{self.reveal}[/b]")


class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Title("[@click=open_docs]Textual Demo[/]")
        yield OptionGroup(
            Option("TOP", ".location-top"),
            Option("First", ".location-first"),
            Option("Baz", ""),
        )

        yield DarkSwitch()


class AboveFold(Container):
    pass


class Section(Container):
    pass


class Column(Container):
    pass


class Text(Static):
    pass


class QuickAccess(Container):
    pass


class LocationLink(Static):
    def __init__(self, label: str, reveal: str) -> None:
        super().__init__(label)
        self.reveal = reveal

    def on_click(self) -> None:
        self.app.query_one(self.reveal).scroll_visible()
        self.app.add_note(f"Scrolling to [b]{self.reveal}[/b]")


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
        self.add_note("Textual Demo app is running")

    def compose(self) -> ComposeResult:
        yield Container(
            Sidebar(classes="-hidden"),
            Header(),
            TextLog(classes="-hidden", wrap=False, highlight=True, markup=True),
            Body(
                QuickAccess(
                    LocationLink("TOP", ".location-top"),
                    LocationLink("First", ".location-first"),
                    LocationLink("Baz", ""),
                ),
                AboveFold(Welcome(), classes="location-top"),
                Column(
                    Section(
                        SectionTitle("CSS"),
                        Text(Markdown(CSS_MD)),
                        Static(
                            Syntax(
                                EXAMPLE_CSS, "css", theme="material", line_numbers=True
                            )
                        ),
                    ),
                    classes="location-first",
                ),
            ),
        )
        yield Footer()


app = DemoApp()
if __name__ == "__main__":
    app.run()
