from textual.app import App
from textual.widgets import Label


class BorderSubtitleAlignApp(App):
    CSS_PATH = "border_subtitle_align.tcss"

    def compose(self):
        lbl = Label("My subtitle is on the left.", id="label1")
        lbl.border_subtitle = "< Left"
        yield lbl

        lbl = Label("My subtitle is centered", id="label2")
        lbl.border_subtitle = "Centered!"
        yield lbl

        lbl = Label("My subtitle is on the right", id="label3")
        lbl.border_subtitle = "Right >"
        yield lbl


if __name__ == "__main__":
    app = BorderSubtitleAlignApp()
    app.run()
