from textual.app import App, ComposeResult
from textual.widgets import Placeholder


class SplitApp(App):
    CSS = """

    #split1 {
        split: right;
        width: 20;
    }

    #split2 {
        split: bottom;
        height: 10;
    }

    #split3 {
        split: top;
        height: 6;
    }

    #split4 {
        split: left;
        width: 30;
    }

    .scrollable {
        height: 5;
    }

    """

    def compose(self) -> ComposeResult:
        yield Placeholder(id="split1")
        yield Placeholder(id="split2")
        yield Placeholder(id="split3")
        yield Placeholder(id="split4")
        yield Placeholder("1", classes="scrollable")
        yield Placeholder("2", classes="scrollable")
        yield Placeholder("3", classes="scrollable")
        yield Placeholder("4", classes="scrollable")
        yield Placeholder("5", classes="scrollable")


if __name__ == "__main__":
    app = SplitApp()
    app.run()
