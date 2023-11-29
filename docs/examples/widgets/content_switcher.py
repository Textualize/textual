from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, ContentSwitcher, DataTable, Markdown

MARKDOWN_EXAMPLE = """# Three Flavours Cornetto

The Three Flavours Cornetto trilogy is an anthology series of British
comedic genre films directed by Edgar Wright.

## Shaun of the Dead

| Flavour | UK Release Date | Director |
| -- | -- | -- |
| Strawberry | 2004-04-09 | Edgar Wright |

## Hot Fuzz

| Flavour | UK Release Date | Director |
| -- | -- | -- |
| Classico | 2007-02-17 | Edgar Wright |

## The World's End

| Flavour | UK Release Date | Director |
| -- | -- | -- |
| Mint | 2013-07-19 | Edgar Wright |
"""


class ContentSwitcherApp(App[None]):
    CSS_PATH = "content_switcher.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal(id="buttons"):  # (1)!
            yield Button("DataTable", id="data-table")  # (2)!
            yield Button("Markdown", id="markdown")  # (3)!

        with ContentSwitcher(initial="data-table"):  # (4)!
            yield DataTable(id="data-table")
            with VerticalScroll(id="markdown"):
                yield Markdown(MARKDOWN_EXAMPLE)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id  # (5)!

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Book", "Year")
        table.add_rows(
            [
                (title.ljust(35), year)
                for title, year in (
                    ("Dune", 1965),
                    ("Dune Messiah", 1969),
                    ("Children of Dune", 1976),
                    ("God Emperor of Dune", 1981),
                    ("Heretics of Dune", 1984),
                    ("Chapterhouse: Dune", 1985),
                )
            ]
        )


if __name__ == "__main__":
    ContentSwitcherApp().run()
