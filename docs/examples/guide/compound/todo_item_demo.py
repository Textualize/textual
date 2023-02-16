from todo_item import TodoItem

from textual.app import App, ComposeResult


class DemoApp(App[None]):
    def compose(self) -> ComposeResult:
        yield TodoItem()


app = DemoApp()

if __name__ == "__main__":
    app.run()
