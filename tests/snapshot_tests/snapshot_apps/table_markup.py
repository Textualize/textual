from textual.app import App, ComposeResult
from textual.widgets import Static

from rich.table import Table


class TableStaticApp(App):
    def compose(self) -> ComposeResult:
        table = Table("[i green]Foo", "Bar", "baz")
        table.add_row("Hello [bold magenta]World!", "[i]Italic", "[u]Underline")
        yield Static(table)


if __name__ == "__main__":
    app = TableStaticApp()
    app.run()
