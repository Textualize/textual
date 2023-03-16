from textual.app import App
from textual.containers import Container, Grid
from textual.widgets import Label


def make_label_container(  # (1)!
    text: str, id: str, border_title: str, border_subtitle: str
) -> Container:
    lbl = Label(text, id=id)
    lbl.border_title = border_title
    lbl.border_subtitle = border_subtitle
    return Container(lbl)


class BorderSubTitleAlignAll(App[None]):
    def compose(self):
        with Grid():
            yield make_label_container(
                "This is the",
                "lbl1",
                "[b]Left, [i]but[/i] it's really long[/]",  # (2)!
                "[u]Left[/]",
            )
            yield make_label_container(
                "story of a Python",
                "lbl2",
                "[b red]Left",  # (3)!
                "[reverse]Center, but it's loooooooooooong.",
            )
            yield make_label_container(
                "developer that",
                "lbl3",
                "[b i on purple]Left[/]",  # (4)!
                "Right",
            )
            yield make_label_container(
                "had to fill up",
                "lbl4",
                "Center",
                "[link=https://textual.textualize.io]Left",  # (5)!
            )
            yield make_label_container("nine labels", "lbl5", "Center", "Center")
            yield make_label_container(
                "and ended up redoing it",
                "lbl6",
                "Center",
                "Right",
            )
            yield make_label_container("because the first try", "lbl7", "Right", "Left")
            yield make_label_container("had some labels", "lbl8", "Right", "Center")
            yield make_label_container(
                "that were too long.",
                "lbl9",
                "Right",
                "Right",
            )


app = BorderSubTitleAlignAll(css_path="border_sub_title_align_all.css")

if __name__ == "__main__":
    app.run()
