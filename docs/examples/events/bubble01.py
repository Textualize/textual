from textual.app import App, ComposeResult

from textual.widgets import Static, TextLog


class BubbleApp(App):

    CSS = """
    

    
    
    """

    def compose(self) -> ComposeResult:
        Static("Foo", id="static")
        yield TextLog()

    def on_key(self) -> None:
        log = self.query_one(TextLog)
        self.query_one(TextLog).write(self.tree)
        log.write(repr((log.size, log.virtual_size)))


app = BubbleApp()
if __name__ == "__main__":
    app.run()
