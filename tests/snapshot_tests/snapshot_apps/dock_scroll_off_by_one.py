from textual.app import App, ComposeResult
from textual.widgets import Checkbox, Footer


class ScrollOffByOne(App):
    def compose(self) -> ComposeResult:
        for number in range(1, 100):
            yield Checkbox(str(number))
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("Screen").scroll_end()


app = ScrollOffByOne()
if __name__ == "__main__":
    app.run()
