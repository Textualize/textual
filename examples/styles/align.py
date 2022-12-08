from textual.app import App
from textual.widgets import Static


class AlignApp(App):
    def compose(self):
        yield Static("Vertical alignment with [b]Textual[/]", classes="box")
        yield Static("Take note, browsers.", classes="box")


app = AlignApp(css_path="align.css")
