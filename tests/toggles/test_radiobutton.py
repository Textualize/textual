from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import RadioButton


class RadioButtonApp(App[None]):
    def __init__(self):
        super().__init__()
        self.events_received = []

    def compose(self) -> ComposeResult:
        yield RadioButton("Test", id="rb1")
        yield RadioButton(id="rb2")
        yield RadioButton(value=True, id="rb3")

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        self.events_received.append(
            (
                event.radio_button.id,
                event.radio_button.value,
                event.radio_button == event.control,
            )
        )


async def test_radio_button_initial_state() -> None:
    """The initial states of the radio buttons should be as we specified."""
    async with RadioButtonApp().run_test() as pilot:
        assert [button.value for button in pilot.app.query(RadioButton)] == [
            False,
            False,
            True,
        ]
        assert [button.has_class("-on") for button in pilot.app.query(RadioButton)] == [
            False,
            False,
            True,
        ]
        assert pilot.app.events_received == []


async def test_radio_button_toggle() -> None:
    """Test the status of the radio buttons after they've been toggled."""
    async with RadioButtonApp().run_test() as pilot:
        for box in pilot.app.query(RadioButton):
            box.toggle()
        assert [button.value for button in pilot.app.query(RadioButton)] == [
            True,
            True,
            False,
        ]
        assert [button.has_class("-on") for button in pilot.app.query(RadioButton)] == [
            True,
            True,
            False,
        ]
        await pilot.pause()
        assert pilot.app.events_received == [
            ("rb1", True, True),
            ("rb2", True, True),
            ("rb3", False, True),
        ]
