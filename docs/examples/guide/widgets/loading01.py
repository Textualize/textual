from asyncio import sleep
from random import randint

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import DataTable

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class DataApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
    }
    DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield DataTable()
        yield DataTable()
        yield DataTable()

    def on_mount(self) -> None:
        for data_table in self.query(DataTable):
            data_table.loading = True  # (1)!
            self.load_data(data_table)

    @work
    async def load_data(self, data_table: DataTable) -> None:
        await sleep(randint(2, 10))  # (2)!
        data_table.add_columns(*ROWS[0])
        data_table.add_rows(ROWS[1:])
        data_table.loading = False  # (3)!


if __name__ == "__main__":
    app = DataApp()
    app.run()
