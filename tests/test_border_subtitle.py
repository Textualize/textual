from textual.app import App, ComposeResult
from textual.widget import Widget


async def test_border_subtitle():
    class BorderWidget(Widget):
        BORDER_TITLE = "foo"
        BORDER_SUBTITLE = "bar"

    class SimpleApp(App):
        def compose(self) -> ComposeResult:
            yield BorderWidget()

    empty_app = SimpleApp()
    async with empty_app.run_test():
        widget = empty_app.query_one(BorderWidget)
        assert widget.border_title == "foo"
        assert widget.border_subtitle == "bar"
