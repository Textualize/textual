from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Static

text = "\n".join("FOO BAR bazz etc sdfsdf " * 20 for n in range(1000))


class Content(Static):
    DEFAULT_CSS = """
    Content {
        width: auto;
    }
    """

    def render(self):
        return Text(text, no_wrap=False)


class ScrollApp(App):
    CSS = """
    Screen {
        overflow: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Content()


app = ScrollApp()
if __name__ == "__main__":
    app.run()
