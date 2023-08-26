from textual.app import App
from textual.widgets import Label


class AllContentAlignApp(App):
    def compose(self):
        yield Label("left top", id="left-top")
        yield Label("center top", id="center-top")
        yield Label("right top", id="right-top")
        yield Label("left middle", id="left-middle")
        yield Label("center middle", id="center-middle")
        yield Label("right middle", id="right-middle")
        yield Label("left bottom", id="left-bottom")
        yield Label("center bottom", id="center-bottom")
        yield Label("right bottom", id="right-bottom")


app = AllContentAlignApp(css_path="content_align_all.tcss")
