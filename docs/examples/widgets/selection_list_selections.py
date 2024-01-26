from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, SelectionList
from textual.widgets.selection_list import Selection


class SelectionListApp(App[None]):
    CSS_PATH = "selection_list.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield SelectionList[int](  # (1)!
            Selection("Falken's Maze", 0, True),
            Selection("Black Jack", 1),
            Selection("Gin Rummy", 2),
            Selection("Hearts", 3),
            Selection("Bridge", 4),
            Selection("Checkers", 5),
            Selection("Chess", 6, True),
            Selection("Poker", 7),
            Selection("Fighter Combat", 8, True),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Shall we play some games?"


if __name__ == "__main__":
    SelectionListApp().run()
