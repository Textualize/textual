from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App):
    def compose(self) -> ComposeResult:
        yield Input("Hello, World!")


async def test_input_clear():
    async with InputApp().run_test() as pilot:
        input_widget = pilot.app.query_one(Input)
        assert input_widget.value == "Hello, World!"
        input_widget.clear()
        await pilot.pause()
        assert input_widget.value == ""
