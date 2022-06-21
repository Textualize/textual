from textual.app import App, ComposeResult
from textual.widgets import DataTable

from rich.syntax import Syntax
from rich.table import Table

CODE = '''\
def loop_first_last(values: Iterable[T]) -> Iterable[tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value'''

test_table = Table(title="Star Wars Movies")

test_table.add_column("Released", style="cyan", no_wrap=True)
test_table.add_column("Title", style="magenta")
test_table.add_column("Box Office", justify="right", style="green")

test_table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
test_table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
test_table.add_row(
    "Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889"
)
test_table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")


class TableApp(App):
    def compose(self) -> ComposeResult:
        table = self.table = DataTable(id="data")
        table.add_column("Foo", width=20)
        table.add_column("Bar", width=60)
        table.add_column("Baz", width=20)
        table.add_column("Foo", width=16)
        table.add_column("Bar", width=16)
        table.add_column("Baz", width=16)

        for n in range(200):
            height = 1
            row = [f"row [b]{n}[/b] col [i]{c}[/i]" for c in range(6)]
            if n == 10:
                row[1] = Syntax(CODE, "python", line_numbers=True, indent_guides=True)
                height = 13

            if n == 30:
                row[1] = test_table
                height = 13
            table.add_row(*row, height=height)
        yield table

    def on_mount(self):
        self.bind("d", "toggle_dark")
        self.bind("z", "toggle_zebra")
        self.bind("x", "exit")

    def action_toggle_dark(self) -> None:
        self.app.dark = not self.app.dark

    def action_toggle_zebra(self) -> None:
        self.table.zebra_stripes = not self.table.zebra_stripes

    def action_exit(self) -> None:
        pass


app = TableApp()
if __name__ == "__main__":
    print(app.run())
