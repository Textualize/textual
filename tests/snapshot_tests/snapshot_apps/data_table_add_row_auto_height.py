from rich.panel import Panel
from rich.text import Text

from textual.app import App
from textual.widgets import DataTable


class AutoHeightRowsApp(App[None]):
    def compose(self):
        table = DataTable()
        self.column = table.add_column("N")
        table.add_column("Column", width=10)
        table.add_row(3, "hey there", height=None)
        table.add_row(1, Text("hey there"), height=None)
        table.add_row(5, Text("long string", overflow="fold"), height=None)
        table.add_row(2, Panel.fit("Hello\nworld"), height=None)
        table.add_row(4, "1\n2\n3\n4\n5\n6\n7", height=None)
        yield table

    def key_s(self):
        self.query_one(DataTable).sort(self.column)


if __name__ == "__main__":
    AutoHeightRowsApp().run()
