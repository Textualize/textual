from textual import events
from textual.app import App
from textual.widgets import Input


async def test_paste_app():
    paste_events = []

    class PasteApp(App):
        def on_paste(self, event):
            paste_events.append(event)

    app = PasteApp()
    async with app.run_test() as pilot:
        app.post_message(events.Paste(text="Hello"))
        await pilot.pause(0)

    assert len(paste_events) == 1
    assert paste_events[0].text == "Hello"


async def test_empty_paste():
    """Regression test for https://github.com/Textualize/textual/issues/2563."""

    paste_events = []

    class MyInput(Input):
        def on_paste(self, event):
            super()._on_paste(event)
            paste_events.append(event)

    class PasteApp(App):
        def compose(self):
            yield MyInput()

        def key_p(self):
            self.query_one(MyInput).post_message(events.Paste(""))

    app = PasteApp()
    async with app.run_test() as pilot:
        app.set_focus(None)
        await pilot.press("p")
        assert app.query_one(MyInput).value == ""
        assert len(paste_events) == 1
        assert paste_events[0].text == ""
