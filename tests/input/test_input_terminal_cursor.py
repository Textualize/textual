from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Input


class InputApp(App):
    # Apply padding to ensure gutter accounted for.
    CSS = "Input { padding: 4 8 }"

    def compose(self) -> ComposeResult:
        # We don't want to select the text on focus, as selected text
        # has different interactions with the cursor_left action.
        yield Input("こんにちは!", select_on_focus=False)


async def test_initial_terminal_cursor_position():
    app = InputApp()
    async with app.run_test():
        # The input is focused so the terminal cursor position should update.
        assert app.cursor_position == Offset(21, 5)


async def test_terminal_cursor_position_update_on_cursor_move():
    app = InputApp()
    async with app.run_test():
        input_widget = app.query_one(Input)
        input_widget.action_cursor_left()
        input_widget.action_cursor_left()
        # We went left over two double-width characters
        assert app.cursor_position == Offset(17, 5)
