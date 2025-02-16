from textual.app import App
from textual.containers import Container, Grid
from textual.widgets import Label


def make_label_container(  # (11)!
    text: str, id: str, border_title: str, border_subtitle: str
) -> Container:
    lbl = Label(text, id=id)
    lbl.border_title = border_title
    lbl.border_subtitle = border_subtitle
    return Container(lbl)


class BorderSubTitleAlignAll(App[None]):
    CSS_PATH = "border_sub_title_align_all.tcss"

    def compose(self):
        with Grid():
            yield make_label_container(  # (1)!
                "This is the story of",
                "lbl1",
                "[b]Border [i]title[/i][/]",
                "[u][r]Border[/r] subtitle[/]",
            )
            yield make_label_container(  # (2)!
                "a Python",
                "lbl2",
                "[b red]Left, but it's loooooooooooong",
                "[reverse]Center, but it's loooooooooooong",
            )
            yield make_label_container(  # (3)!
                "developer that",
                "lbl3",
                "[b i on purple]Left[/]",
                "[r u white on black]@@@[/]",
            )
            yield make_label_container(
                "had to fill up",
                "lbl4",
                "",  # (4)!
                "[link='https://textual.textualize.io']Left[/]",  # (5)!
            )
            yield make_label_container(  # (6)!
                "nine labels", "lbl5", "Title", "Subtitle"
            )
            yield make_label_container(  # (7)!
                "and ended up redoing it",
                "lbl6",
                "Title",
                "Subtitle",
            )
            yield make_label_container(  # (8)!
                "because the first try",
                "lbl7",
                "Title, but really loooooooooong!",
                "Subtitle, but really loooooooooong!",
            )
            yield make_label_container(  # (9)!
                "had some labels",
                "lbl8",
                "Title, but really loooooooooong!",
                "Subtitle, but really loooooooooong!",
            )
            yield make_label_container(  # (10)!
                "that were too long.",
                "lbl9",
                "Title, but really loooooooooong!",
                "Subtitle, but really loooooooooong!",
            )


if __name__ == "__main__":
    app = BorderSubTitleAlignAll()
    app.run()
