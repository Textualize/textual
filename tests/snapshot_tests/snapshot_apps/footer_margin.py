from textual.app import App, ComposeResult
from textual.widgets import Footer


class FooterMarginApp(App):
    """Regression test for https://github.com/Textualize/textual/issues/6616

    Setting a margin on the Footer should shrink it on all sides. Previously
    the Footer kept a fixed width, so the left/top margin created a gap but
    the right margin had nowhere to go and was invisible."""

    CSS = """
    Screen {
        background: blue;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Footer).styles.margin = 5


if __name__ == "__main__":
    app = FooterMarginApp()
    app.run()