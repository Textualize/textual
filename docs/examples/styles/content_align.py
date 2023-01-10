from textual.app import App
from textual.widgets import Label


class ContentAlignApp(App):
    def compose(self):
        yield Label("With [i]content-align[/] you can...", id="box1")
        yield Label("...[b]Easily align content[/]...", id="box2")
        yield Label("...Horizontally [i]and[/] vertically!", id="box3")


app = ContentAlignApp(css_path="content_align.css")
