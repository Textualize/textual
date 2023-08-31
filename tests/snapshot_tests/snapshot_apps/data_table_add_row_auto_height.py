from rich.panel import Panel
from rich.text import Text

from textual.app import App
from textual.widgets import DataTable


class AutoHeightRowsApp(App[None]):
    def compose(self):
        table = DataTable()
        table.add_column("Column", width=10)
        table.add_row("hey there", height=None)
        table.add_row(Text("hey there"), height=None)
        table.add_row(Text("long string", overflow="fold"), height=None)
        table.add_row(Panel.fit("Hello\nworld"), height=None)
        table.add_row("1\n2\n3\n4\n5\n6\n7", height=None)
        yield table


if __name__ == "__main__":
    AutoHeightRowsApp().run()
