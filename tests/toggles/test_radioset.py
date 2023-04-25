from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import RadioButton, RadioSet


class RadioSetApp(App[None]):
    def __init__(self):
        super().__init__()
        self.events_received = []

    def compose(self) -> ComposeResult:
        with RadioSet(id="from_buttons"):
            yield RadioButton()
            yield RadioButton()
            yield RadioButton(value=True)
        yield RadioSet("One", "True", "Three", id="from_strings")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.events_received.append(
            (
                event.radio_set.id,
                event.index,
                [button.value for button in event.radio_set.query(RadioButton)],
            )
        )


async def test_radio_sets_initial_state():
    """The initial states of the radio sets should be as we specified."""
    async with RadioSetApp().run_test() as pilot:
        assert pilot.app.query_one("#from_buttons", RadioSet).pressed_index == 2
        assert pilot.app.query_one("#from_buttons", RadioSet).pressed_button is not None
        assert pilot.app.query_one("#from_strings", RadioSet).pressed_index == -1
        assert pilot.app.query_one("#from_strings", RadioSet).pressed_button is None
        assert pilot.app.events_received == []


async def test_radio_sets_toggle():
    """Test the status of the radio sets after they've been toggled."""
    async with RadioSetApp().run_test() as pilot:
        pilot.app.query_one("#from_buttons", RadioSet)._nodes[0].toggle()
        pilot.app.query_one("#from_strings", RadioSet)._nodes[2].toggle()
        await pilot.pause()
        assert pilot.app.query_one("#from_buttons", RadioSet).pressed_index == 0
        assert pilot.app.query_one("#from_buttons", RadioSet).pressed_button is not None
        assert pilot.app.query_one("#from_strings", RadioSet).pressed_index == 2
        assert pilot.app.query_one("#from_strings", RadioSet).pressed_button is not None
        assert pilot.app.events_received == [
            ("from_buttons", 0, [True, False, False]),
            ("from_strings", 2, [False, False, True]),
        ]


async def test_radioset_inner_navigation():
    """Using the cursor keys should navigate between buttons in a set."""
    async with RadioSetApp().run_test() as pilot:
        assert pilot.app.screen.focused is None
        await pilot.press("tab")
        for key, landing in (("down", 1), ("up", 0), ("right", 1), ("left", 0)):
            await pilot.press(key, "enter")
            assert (
                pilot.app.query_one("#from_buttons", RadioSet).pressed_button
                == pilot.app.query_one("#from_buttons").children[landing]
            )


async def test_radioset_breakout_navigation():
    """Shift/Tabbing while in a radioset should move to the previous/next focsuable after the set itself."""
    async with RadioSetApp().run_test() as pilot:
        assert pilot.app.screen.focused is None
        await pilot.press("tab")
        assert pilot.app.screen.focused is pilot.app.query_one("#from_buttons")
        await pilot.press("tab")
        assert pilot.app.screen.focused is pilot.app.query_one("#from_strings")
        await pilot.press("shift+tab")
        assert pilot.app.screen.focused is pilot.app.query_one("#from_buttons")


class BadRadioSetApp(App[None]):
    def compose(self) -> ComposeResult:
        with RadioSet():
            for n in range(20):
                yield RadioButton(str(n), True)


async def test_there_can_only_be_one():
    """Adding multiple 'on' buttons should result in only one on."""
    async with BadRadioSetApp().run_test() as pilot:
        assert len(pilot.app.query("RadioButton.-on")) == 1
        assert pilot.app.query_one(RadioSet).pressed_index == 0
