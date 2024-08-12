from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label

LORUM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."


class ExampleApp(App):
    CSS = """
    Screen {
       
        DataTable {
            border: solid white;
        }
    }

    """

    def compose(self) -> ComposeResult:
        yield Label("automatic scrollbar")
        yield DataTable(id="table1")
        yield Label("no automatic scrollbar")
        yield DataTable(id="table2")

    def on_mount(self) -> None:
        table = self.query_one("#table1", DataTable)
        table.add_column("Column 1")
        table.add_column("Column 2")
        table.add_row(LORUM_IPSUM, LORUM_IPSUM)

        table = self.query_one("#table2", DataTable)
        table.add_column("Column 1")
        table.add_column("Column 2")
        table.add_row("Paul", "Jessica")


if __name__ == "__main__":
    app = ExampleApp()
    app.run()
