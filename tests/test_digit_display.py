from textual.app import App, ComposeResult
from textual.widgets import DigitDisplay


async def test_digit_display_when_content_updated_then_display_widgets_update_accordingly():
    class DigitDisplayApp(App):
        def compose(self) -> ComposeResult:
            yield DigitDisplay("3.14159")

    app = DigitDisplayApp()

    async with app.run_test() as pilot:
        w: DigitDisplay = app.query_one(DigitDisplay)
        assert w.digits == "3.14159"
        assert len(w._displays) == len(w.digits)
        assert w.digits == "".join(w.digit for w in w._displays)
