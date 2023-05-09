from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Checkbox


class CheckboxApp(App[None]):
    def __init__(self):
        super().__init__()
        self.events_received = []

    def compose(self) -> ComposeResult:
        yield Checkbox("Test", id="cb1")
        yield Checkbox(id="cb2")
        yield Checkbox(value=True, id="cb3")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.events_received.append(
            (event.checkbox.id, event.checkbox.value, event.checkbox == event.control)
        )


async def test_checkbox_initial_state() -> None:
    """The initial states of the check boxes should be as we specified."""
    async with CheckboxApp().run_test() as pilot:
        assert [box.value for box in pilot.app.query(Checkbox)] == [False, False, True]
        assert [box.has_class("-on") for box in pilot.app.query(Checkbox)] == [
            False,
            False,
            True,
        ]
        assert pilot.app.events_received == []


async def test_checkbox_toggle() -> None:
    """Test the status of the check boxes after they've been toggled."""
    async with CheckboxApp().run_test() as pilot:
        for box in pilot.app.query(Checkbox):
            box.toggle()
        assert [box.value for box in pilot.app.query(Checkbox)] == [True, True, False]
        assert [box.has_class("-on") for box in pilot.app.query(Checkbox)] == [
            True,
            True,
            False,
        ]
        await pilot.pause()
        assert pilot.app.events_received == [
            ("cb1", True, True),
            ("cb2", True, True),
            ("cb3", False, True),
        ]
