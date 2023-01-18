from textual.app import App
from textual.coordinate import Coordinate
from textual.widgets import DataTable


class DataTableApp(App):
    def compose(self):
        yield DataTable()


async def test_clear():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.cursor_cell == Coordinate(0, 0)
        assert table.hover_cell == Coordinate(0, 0)

        # Add some data and update cursor positions
        table.add_column("Column0")
        table.add_rows([["Row0"], ["Row1"], ["Row2"]])
        table.cursor_cell = Coordinate(1, 0)
        table.hover_cell = Coordinate(2, 0)

        # Ensure the cursor positions are reset to origin on clear()
        table.clear()
        assert table.cursor_cell == Coordinate(0, 0)
        assert table.hover_cell == Coordinate(0, 0)

        # Ensure that the table has been cleared
        assert table.data == {}
        assert table.rows == {}
        assert len(table.columns) == 1

        # Clearing the columns too
        table.clear(columns=True)
        assert len(table.columns) == 0
