from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.tui.app import App
from rich.tui.view import View

from rich.widgets.color_changer import ColorChanger


class SimpleApp(App):
    table: Table

    def __init__(
        self,
        console: Console = None,
        view: View = None,
        screen: bool = True,
    ):
        super().__init__(console, view, screen, title='Simple App')

        self.table = table = Table("foo", "bar", "baz")
        table.add_row("1", "2", "3")

    def visualize(self):
        layout = Layout()
        layout.split_column(
            Layout(self.table, name="top"), Layout(ColorChanger(), name="bottom")
        )
        layout["bottom"].split_row(Layout(name="left"), Layout(name="right"))
        return layout


if __name__ == "__main__":
    app = SimpleApp()
    app.run()
