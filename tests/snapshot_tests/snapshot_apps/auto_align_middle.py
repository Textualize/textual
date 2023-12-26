from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label


class AutoAlignMiddleApp(App[None]):
    CSS = """
    .outer > * {
        height: auto;
        align: center middle;
    }

    .outer > * > * {
        height: auto;
    }

    .even {
        background: $primary;
    }
    
    .odd {
        background: $primary-lighten-3;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(classes="outer"):
            for i in range(5):
                with Horizontal(classes="even" if i % 2 == 0 else "odd"):
                    yield Label("This is line {}".format(i + 1))


if __name__ == "__main__":
    app = AutoAlignMiddleApp()
    app.run()
