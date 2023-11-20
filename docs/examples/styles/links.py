from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """\
Here is a [@click='app.bell']link[/] which you can click!
"""


class LinksApp(App):
    CSS_PATH = "links.tcss"

    def compose(self) -> ComposeResult:
        yield Static(TEXT)
        yield Static(TEXT, id="custom")


if __name__ == "__main__":
    app = LinksApp()
    app.run()
