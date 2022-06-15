from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    def compose(self) -> ComposeResult:
        table = self.table = DataTable(id="data")
        table.add_column("Foo", width=16)
        table.add_column("Bar", width=16)
        table.add_column("Baz", width=16)
        table.add_column("Egg", width=16)
        table.add_column("Foo", width=16)
        table.add_column("Bar", width=16)
        table.add_column("Baz", width=16)
        table.add_column("Egg", width=16)

        for n in range(100):
            row = [f"row [b]{n}[/b] col [i]{c}[/i]" for c in range(8)]
            table.add_row(*row)
        yield table

    def on_mount(self):
        self.bind("d", "toggle_dark")
        self.bind("z", "toggle_zebra")

    def action_toggle_dark(self) -> None:
        self.app.dark = not self.app.dark

    def action_toggle_zebra(self) -> None:
        self.table.zebra_stripes = not self.table.zebra_stripes


app = TableApp()
if __name__ == "__main__":
    app.run()
