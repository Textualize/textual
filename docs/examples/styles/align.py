from textual.app import App
from textual.widgets import Label


class AlignApp(App):
    def compose(self):
        yield Label("Vertical alignment with [b]Textual[/]", classes="box")
        yield Label("Take note, browsers.", classes="box")


app = AlignApp(css_path="align.css")
