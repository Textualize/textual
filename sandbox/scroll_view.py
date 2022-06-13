from textual.app import App, ComposeResult
from textual.scroll_view import ScrollView


class ScrollApp(App):
    def compose(self) -> ComposeResult:
        yield ScrollView()


app = ScrollApp()
app.run()
