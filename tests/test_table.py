import asyncio

from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()


async def test_table_clear() -> None:
    """Check DataTable.clear"""

    app = TableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.add_columns("foo", "bar")
        assert table.row_count == 0
        table.add_row("Hello", "World!")
        assert [col.label for col in table.columns] == [Text("foo"), Text("bar")]
        assert table.data == {0: ["Hello", "World!"]}
        assert table.row_count == 1
        table.clear()
        assert [col.label for col in table.columns] == [Text("foo"), Text("bar")]
        assert table.data == {}
        assert table.row_count == 0


async def test_table_clear_with_columns() -> None:
    """Check DataTable.clear(columns=True)"""

    app = TableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.add_columns("foo", "bar")
        assert table.row_count == 0
        table.add_row("Hello", "World!")
        assert [col.label for col in table.columns] == [Text("foo"), Text("bar")]
        assert table.data == {0: ["Hello", "World!"]}
        assert table.row_count == 1
        table.clear(columns=True)
        assert [col.label for col in table.columns] == []
        assert table.data == {}
        assert table.row_count == 0

async def test_table_add_row() -> None:

    app = TableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("foo", "bar")

        assert table.columns[0].width == 3
        assert table.columns[1].width == 3
        table.add_row("Hello", "World!")
        await asyncio.sleep(0)
        assert table.columns[0].content_width == 5
        assert table.columns[1].content_width == 6

        table.add_row("Hello World!!!", "fo")
        await asyncio.sleep(0)
        assert table.columns[0].content_width == 14
        assert table.columns[1].content_width == 6
