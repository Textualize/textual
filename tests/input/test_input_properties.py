from __future__ import annotations

from rich.highlighter import JSONHighlighter
from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input


class InputApp(App[None]):
    TEST_TEXT = "Let's rock!"

    CSS = """
    Container, Input {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Input(self.TEST_TEXT)


async def test_internal_value_no_password():
    """The displayed value should be the input value."""
    async with InputApp().run_test() as pilot:
        assert pilot.app.query_one(Input)._value == Text(pilot.app.TEST_TEXT)


async def test_internal_value_password():
    """The displayed value should be a password text."""
    async with InputApp().run_test() as pilot:
        pilot.app.query_one(Input).password = True
        assert pilot.app.query_one(Input)._value == Text("•" * len(pilot.app.TEST_TEXT))


async def test_internal_value_highlighted():
    async with InputApp().run_test() as pilot:
        pilot.app.query_one(Input).highlighter = JSONHighlighter()
        test_text = f'{{"test": "{pilot.app.TEST_TEXT}"}}'
        pilot.app.query_one(Input).value = test_text
        assert pilot.app.query_one(Input)._value == JSONHighlighter()(test_text)


async def test_cursor_toggle():
    """Cursor toggling should toggle the cursor."""
    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        input_widget.cursor_blink = False
        assert input_widget._cursor_visible is True
        input_widget._toggle_cursor()
        assert input_widget._cursor_visible is False


async def test_input_height():
    """Height should be 1 even if set to auto."""
    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        assert (
            input_widget.styles.height.value == input_widget.parent.styles.height.value
        )
        assert input_widget.parent.styles.height.value == 1
