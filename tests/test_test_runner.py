from textual import events
from textual.app import App


async def test_run_test() -> None:
    """Test the run_test context manager."""
    keys_pressed: list[str] = []

    class TestApp(App[str]):
        def on_key(self, event: events.Key) -> None:
            keys_pressed.append(event.key)

    app = TestApp()
    async with app.run_test() as pilot:
        assert (
            str(pilot) == "<Pilot app=TestApp(title='TestApp', classes={'-dark-mode'})>"
        )
        await pilot.press("tab", *"foo")
        await pilot.exit("bar")

    assert app.return_value == "bar"
    assert keys_pressed == ["tab", "f", "o", "o"]
