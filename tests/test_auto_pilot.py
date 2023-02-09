from textual import events
from textual.app import App
from textual.pilot import Pilot


def test_auto_pilot() -> None:
    keys_pressed: list[str] = []

    class TestApp(App):
        def on_key(self, event: events.Key) -> None:
            keys_pressed.append(event.key)

    async def auto_pilot(pilot: Pilot) -> None:
        await pilot.press("tab", *"foo")
        await pilot.exit("bar")

    app = TestApp()
    result = app.run(headless=True, auto_pilot=auto_pilot)
    assert result == "bar"
    assert keys_pressed == ["tab", "f", "o", "o"]
