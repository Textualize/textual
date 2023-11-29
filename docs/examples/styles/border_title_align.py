from textual.app import App
from textual.widgets import Label


class BorderTitleAlignApp(App):
    CSS_PATH = "border_title_align.tcss"

    def compose(self):
        lbl = Label("My title is on the left.", id="label1")
        lbl.border_title = "< Left"
        yield lbl

        lbl = Label("My title is centered", id="label2")
        lbl.border_title = "Centered!"
        yield lbl

        lbl = Label("My title is on the right", id="label3")
        lbl.border_title = "Right >"
        yield lbl


if __name__ == "__main__":
    app = BorderTitleAlignApp()
    app.run()
