from textual.app import App
from textual.widgets import Static


class ContentAlignApp(App):
    def compose(self):
        yield Static("With [i]content-align[/] you can...", id="box1")
        yield Static("...[b]Easily align content[/]...", id="box2")
        yield Static("...Horizontally [i]and[/] vertically!", id="box3")


app = ContentAlignApp(css_path="content_align.css")
