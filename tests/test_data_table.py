from textual.app import App
from textual.coordinate import Coordinate
from textual.message import Message
from textual.widgets import DataTable


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
        table.add_rows([["0/0", "0/1"], ["1/0", "1/1"], ["2/0", "2/1"]])

        # A CellHighlighted is emitted because there were no rows (and
        # therefore no highlighted cells), but then a row was added, and
        # so the cell at (0, 0) became highlighted.
        expected_messages.append("CellHighlighted")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # Pressing Enter when the cursor is on a cell emits a CellSelected
        await pilot.press("enter")
        expected_messages.append("CellSelected")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # Moving the cursor left and up when the cursor is at origin
        # emits no events, since the cursor doesn't move at all.
        await pilot.press("left", "up")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # ROW CURSOR
        # Switch over to the row cursor... should emit a `RowHighlighted`
        table.cursor_type = "row"
        expected_messages.append("RowHighlighted")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # Select the row...
        await pilot.press("enter")
        expected_messages.append("RowSelected")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # COLUMN CURSOR
        # Switching to the column cursor emits a `ColumnHighlighted`
        table.cursor_type = "column"
        expected_messages.append("ColumnHighlighted")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # Select the column...
        await pilot.press("enter")
        expected_messages.append("ColumnSelected")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # NONE CURSOR
        # No messages get emitted at all...
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause(2 / 100)
        # No new messages since cursor not visible
        assert messages == expected_messages

        # Edge case - if show_cursor is False, and the cursor type
        # is changed back to a visible type, then no messages should
        # be emitted since the cursor is still not visible.
        table.show_cursor = False
        table.cursor_type = "cell"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause(2 / 100)
        # No new messages since show_cursor = False
        assert messages == expected_messages

        # Now when show_cursor is set back to True, the appropriate
        # message should be emitted for highlighting the cell.
        table.show_cursor = True
        expected_messages.append("CellHighlighted")
        await pilot.pause(2 / 100)
        assert messages == expected_messages

        # Likewise, if the cursor_type is "none", and we change the
        # show_cursor to True, then no events should be raised since
        # the cursor is still not visible to the user.
        table.cursor_type = "none"
        await pilot.press("up", "down", "left", "right", "enter")
        await pilot.pause(2 / 100)
        assert messages == expected_messages


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
