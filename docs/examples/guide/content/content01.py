from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT1 = """\
Hello, [bold $text on $primary]World[/]!

[@click=app.notify('Hello, World!')]Click me[/]
"""

TEXT2 = """\
Markup will [bold]not[/bold] be displayed.

Tags will be left in the output.

"""


class ContentApp(App):
    CSS = """
    Screen {
        Static {
            height: 1fr;
        }
        #text1 { background: $primary-muted; }
        #text2 { background: $error-muted; }
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(TEXT1, id="text1")
        yield Static(TEXT2, id="text2", markup=False)  # (1)!


if __name__ == "__main__":
    app = ContentApp()
    app.run()
