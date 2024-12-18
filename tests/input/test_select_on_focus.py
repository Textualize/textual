"""The standard path of selecting text on focus is well covered by snapshot tests."""

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.widgets.input import Selection


class InputApp(App[None]):
    """An app with an input widget."""

    def compose(self) -> ComposeResult:
        yield Input("Hello, world!")


async def test_focus_from_app_focus_does_not_select():
    """When an Input has focused and the *app* is blurred and then focused (e.g. by pressing
    alt+tab or focusing another terminal pane), then the content of the Input should not be
    fully selected when `Input.select_on_focus=True`.
    """
    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        input_widget.focus()
        input_widget.selection = Selection.cursor(0)
        assert input_widget.selection == Selection.cursor(0)
        pilot.app.post_message(events.AppBlur())
        await pilot.pause()
        pilot.app.post_message(events.AppFocus())
        await pilot.pause()
        assert input_widget.selection == Selection.cursor(0)
