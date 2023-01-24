import pytest
from rich.text import Text

from textual.app import App
from textual.coordinate import Coordinate
from textual.message import Message
from textual.widgets import DataTable
from textual.widgets._data_table import (
    StringKey,
    CellDoesNotExist,
    RowKey,
    Row,
    ColumnKey,
)

ROWS = [["0/0", "0/1"], ["1/0", "1/1"], ["2/0", "2/1"]]


class DataTableApp(App):
    messages = []
    messages_to_record = {
        "CellHighlighted",
        "CellSelected",
        "RowHighlighted",
        "RowSelected",
        "ColumnHighlighted",
        "ColumnSelected",
    }

    def compose(self):
        table = DataTable()
        table.focus()
        yield table

    def record_data_table_event(self, message: Message) -> None:
        name = message.__class__.__name__
        if name in self.messages_to_record:
            self.messages.append(name)

    async def _on_message(self, message: Message) -> None:
        await super()._on_message(message)
        self.record_data_table_event(message)


async def test_datatable_message_emission():
    app = DataTableApp()
    messages = app.messages
    expected_messages = []
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)

        assert messages == expected_messages

        table.add_columns("Column0", "Column1")
        table.add_rows(ROWS)

        # A CellHighlighted is emitted because there were no rows (and
        # therefore no highlighted cells), but then a row was added, and
        # so the cell at (0, 0) became highlighted.
        expected_messages.append("CellHighlighted")
        assert messages == expected_messages

        # Pressing Enter when the cursor is on a cell emits a CellSelected
        await pilot.press("enter")
        expected_messages.append("CellSelected")
        assert messages == expected_messages

        # Moving the cursor left and up when the cursor is at origin
        # emits no events, since the cursor doesn't move at all.
        await pilot.press("left", "up")
        assert messages == expected_messages

        # ROW CURSOR
        # Switch over to the row cursor... should emit a `RowHighlighted`
        table.cursor_type = "row"
        expected_messages.append("RowHighlighted")
        assert messages == expected_messages

        # Select the row...
        await pilot.press("enter")
        expected_messages.append("RowSelected")
        assert messages == expected_messages

        # COLUMN CURSOR
        # Switching to the column cursor emits a `ColumnHighlighted`
        table.cursor_type = "column"
        expected_messages.append("ColumnHighlighted")
        assert messages == expected_messages

        # Select the column...
        await pilot.press("enter")
        expected_messages.append("ColumnSelected")
        assert messages == expected_messages

        # NONE CURSOR
        # No messages get emitted at all...
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        # No new messages since cursor not visible
        assert messages == expected_messages

        # Edge case - if show_cursor is False, and the cursor type
        # is changed back to a visible type, then no messages should
        # be emitted since the cursor is still not visible.
        table.show_cursor = False
        table.cursor_type = "cell"
        await pilot.press("up", "down", "left", "right", "enter")
        # No new messages since show_cursor = False
        assert messages == expected_messages

        # Now when show_cursor is set back to True, the appropriate
        # message should be emitted for highlighting the cell.
        table.show_cursor = True
        expected_messages.append("CellHighlighted")
        assert messages == expected_messages

        # Likewise, if the cursor_type is "none", and we change the
        # show_cursor to True, then no events should be raised since
        # the cursor is still not visible to the user.
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        assert messages == expected_messages


async def test_add_rows():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        row_keys = table.add_rows(ROWS)
        # We're given a key for each row
        assert len(row_keys) == len(ROWS)
        assert len(row_keys) == len(table.data)
        assert table.row_count == len(ROWS)
        # Each key can be used to fetch a row from the DataTable
        assert all(key in table.data for key in row_keys)
        # Ensure the keys are returned *in order*, and there's one for each row
        for key, row in zip(row_keys, range(len(ROWS))):
            assert table.rows[key].index == row


async def test_add_rows_user_defined_keys():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        algernon_key = table.add_row(*ROWS[0], key="algernon")
        table.add_row(*ROWS[1], key="charlie")
        auto_key = table.add_row(*ROWS[2])

        assert algernon_key == "algernon"
        # We get a RowKey object back, but we can use our own string *or* this object
        # to find the row we're looking for, they're considered equivalent for lookups.
        assert isinstance(algernon_key, RowKey)
        assert table.data[algernon_key] == ROWS[0]
        assert table.data["algernon"] == ROWS[0]
        assert table.data["charlie"] == ROWS[1]
        assert table.data[auto_key] == ROWS[2]

        first_row = Row(algernon_key, index=0, height=1, y=0)
        assert table.rows[algernon_key] == first_row
        assert table.rows["algernon"] == first_row


async def test_add_columns():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        column_keys = table.add_columns("1", "2", "3")
        assert len(column_keys) == 3
        assert len(table.columns) == 3


# TODO: Ensure we can use the key to retrieve the column.
async def test_add_columns_user_defined_keys():
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        key = table.add_column("Column", key="donut")
        assert key == "donut"
        assert key == key


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
        assert table.row_count == 0
        assert len(table.columns) == 1

        # Clearing the columns too
        table.clear(columns=True)
        assert len(table.columns) == 0


async def test_column_labels() -> None:
    app = DataTableApp()
    async with app.run_test():
        table = app.query_one(DataTable)
        table.add_columns("1", "2", "3")
        assert [col.label for col in table.columns] == [Text("1"), Text("2"), Text("3")]


async def test_column_widths() -> None:
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.add_columns("foo", "bar")

        assert table.columns[0].width == 3
        assert table.columns[1].width == 3
        table.add_row("Hello", "World!")
        await pilot.pause()
        assert table.columns[0].content_width == 5
        assert table.columns[1].content_width == 6

        table.add_row("Hello World!!!", "fo")
        await pilot.pause()
        assert table.columns[0].content_width == 14
        assert table.columns[1].content_width == 6


def test_get_cell_value_returns_value_at_cell():
    table = DataTable()
    table.add_rows(ROWS)
    assert table.get_cell_value(Coordinate(0, 0)) == "0/0"


def test_get_cell_value_exception():
    table = DataTable()
    table.add_rows(ROWS)
    with pytest.raises(CellDoesNotExist):
        table.get_cell_value(Coordinate(9999, 0))


def test_key_equals_equivalent_string():
    text = "Hello"
    key = StringKey(text)
    assert key == text
    assert hash(key) == hash(text)


def test_key_doesnt_match_non_equal_string():
    key = StringKey("123")
    text = "laksjdlaskjd"
    assert key != text
    assert hash(key) != hash(text)


def test_key_equals_self():
    row_key = RowKey()
    column_key = ColumnKey()
    assert row_key == row_key
    assert column_key == column_key
    assert row_key != column_key


def test_key_string_lookup():
    # Indirectly covered by other tests, but let's explicitly document
    # in tests how we intend for the keys to work for cache lookups.
    dictionary = {
        "foo": "bar",
        StringKey("hello"): "world",
    }
    assert dictionary["foo"] == "bar"
    assert dictionary[StringKey("foo")] == "bar"
    assert dictionary["hello"] == "world"
    assert dictionary[StringKey("hello")] == "world"
