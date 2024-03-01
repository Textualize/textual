from operator import attrgetter

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label


class Number(Label):
    DEFAULT_CSS = """
    Number {
        width: 1fr;
    }
    """

    def __init__(self, number: int) -> None:
        self.number = number
        super().__init__(classes=f"number{number}")

    def render(self) -> str:
        return str(self.number)


class NumberList(Vertical):

    DEFAULT_CSS = """
    NumberList {
        width: 1fr;
        Number {
            border: green;
            box-sizing: border-box;
            &.number1 {
                height: 3;
            }
            &.number2 {
                height: 4;
            }
            &.number3 {
                height: 5;
            }
            &.number4 {
                height: 6;
            }
            &.number5 {
                height: 7;
            }
        }
    }

    """

    def compose(self) -> ComposeResult:
        yield Number(5)
        yield Number(1)
        yield Number(3)
        yield Number(2)
        yield Number(4)


class SortApp(App):

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield NumberList(id="unsorted")
            yield NumberList(id="ascending")
            yield NumberList(id="descending")

    def on_mount(self) -> None:
        self.query_one("#ascending").sort_children(
            key=attrgetter("number"),
        )
        self.query_one("#descending").sort_children(
            key=attrgetter("number"),
            reverse=True,
        )


if __name__ == "__main__":
    app = SortApp()
    app.run()
