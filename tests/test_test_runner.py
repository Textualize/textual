from textual.app import App
from textual import events


async def test_run_test() -> None:
    """Test the run_test context manager."""
    keys_pressed: list[str] = []

    class TestApp(App[str]):
        def on_key(self, event: events.Key) -> None:
            keys_pressed.append(event.key)

    app = TestApp()
    async with app.run_test() as pilot:
        assert str(pilot) == "<Pilot app=TestApp(title='TestApp')>"
        await pilot.press("tab", *"foo")
        await pilot.pause(1 / 100)
        await pilot.exit("bar")

    assert app.return_value == "bar"
    assert keys_pressed == ["tab", "f", "o", "o"]
