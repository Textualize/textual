from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """\
Here is a [@click='app.bell']link[/] which you can click!
"""


class LinksApp(App):
    def compose(self) -> ComposeResult:
        yield Static(TEXT)
        yield Static(TEXT, id="custom")


app = LinksApp(css_path="links.css")
