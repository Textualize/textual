from textual.app import App
from textual.widgets import Label


class ContentAlignApp(App):
    CSS_PATH = "content_align.tcss"

    def compose(self):
        yield Label("With [i]content-align[/] you can...", id="box1")
        yield Label("...[b]Easily align content[/]...", id="box2")
        yield Label("...Horizontally [i]and[/] vertically!", id="box3")


if __name__ == "__main__":
    app = ContentAlignApp()
    app.run()
