from textual.app import App, ComposeResult
from textual.widgets import LedDisplay


async def test_led_display_when_content_updated_then_display_widgets_update_accordingly():
    class LedDisplayApp(App):
        def compose(self) -> ComposeResult:
            yield LedDisplay("3.14159")

    app = LedDisplayApp()

    async with app.run_test() as pilot:
        w: LedDisplay = app.query_one(LedDisplay)
        assert w.digits == "3.14159"
        assert len(w._displays) == len(w.digits)
        assert w.digits == "".join(w.digit for w in w._displays)

        w.digits = "AbCdEf"
        assert len(w._displays) == len(w.digits)
        assert w.digits == "".join(w.digit for w in w._displays)

        w.digits = "AbCdEfGhIjKlMnOpQrStUvWxYz"
        assert len(w._displays) == len(w.digits)
        assert w.digits == "".join(w.digit for w in w._displays)


async def test_led_display_when_allow_lower_then_add_class_allow_lower():
    class LedDisplayApp(App):
        def compose(self) -> ComposeResult:
            yield LedDisplay(allow_lower=True, id="allowed")
            yield LedDisplay(allow_lower=False, id="all_upper")
            yield LedDisplay(id="default")

    app = LedDisplayApp()

    async with app.run_test() as pilot:
        w: LedDisplay = app.query_one("#allowed")
        assert w.allow_lower
        assert w.has_class("allow_lower")

        w: LedDisplay = app.query_one("#all_upper")
        assert not w.allow_lower
        assert not w.has_class("allow_lower")

        w: LedDisplay = app.query_one("#default")
        assert not w.allow_lower
        assert not w.has_class("allow_lower")
