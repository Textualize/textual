from textual.app import App, ComposeResult

from textual.containers import Container


class ScrollApp(App):

    def compose(self) -> ComposeResult:
        yield Container(
            Container(), Container(),
        id="top")

    def key_r(self) -> None:
        self.query_one("#top").remove()

if __name__ == "__main__":
    app = ScrollApp()
    app.run()
