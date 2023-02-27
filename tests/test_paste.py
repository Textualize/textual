from textual import events
from textual.app import App


async def test_paste_app():
    paste_events = []

    class PasteApp(App):
        def on_paste(self, event):
            paste_events.append(event)

    app = PasteApp()
    async with app.run_test() as pilot:
        await app.post_message(events.Paste(sender=app, text="Hello"))
        await pilot.pause(0)

    assert len(paste_events) == 1
    assert paste_events[0].text == "Hello"
