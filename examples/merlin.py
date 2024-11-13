from __future__ import annotations

import random
from datetime import timedelta
from time import monotonic

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.reactive import var
from textual.renderables.gradient import LinearGradient
from textual.widget import Widget
from textual.widgets import Digits, Label, Switch

# A nice rainbow of colors.
COLORS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    "#ee9944",
    "#eedd00",
    "#99dd55",
    "#44dd88",
    "#22ccbb",
    "#00bbcc",
    "#0099cc",
    "#3366bb",
    "#663399",
]


# Maps a switch number on to other switch numbers, which should be toggled.
TOGGLES: dict[int, tuple[int, ...]] = {
    1: (2, 4, 5),
    2: (1, 3),
    3: (2, 5, 6),
    4: (1, 7),
    5: (2, 4, 6, 8),
    6: (3, 9),
    7: (4, 5, 8),
    8: (7, 9),
    9: (5, 6, 8),
}


class LabelSwitch(Widget):
    """Switch with a numeric label."""

    DEFAULT_CSS = """
    LabelSwitch Label {
        text-align: center;
        width: 1fr;
        text-style: bold;
    }

    LabelSwitch Label#label-5 {
        color: $text-disabled;
    }
    """

    def __init__(self, switch_no: int) -> None:
        self.switch_no = switch_no
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the label and a switch."""
        yield Label(str(self.switch_no), id=f"label-{self.switch_no}")
        yield Switch(id=f"switch-{self.switch_no}", name=str(self.switch_no))


class Timer(Digits):
    """Displays a timer that stops when you win."""

    DEFAULT_CSS = """
    Timer {
        text-align: center;
        width: auto;
        margin: 2 8;
        color: $warning;
        &:light {
            color: $secondary;
        }
    }
    """
    start_time = var(0.0)
    running = var(True)

    def on_mount(self) -> None:
        """Start the timer on mount."""
        self.start_time = monotonic()
        self.set_interval(1, self.tick)
        self.tick()

    def tick(self) -> None:
        """Called from `set_interval` to update the clock."""
        if self.start_time == 0 or not self.running:
            return
        time_elapsed = timedelta(seconds=int(monotonic() - self.start_time))
        self.update(str(time_elapsed))


class MerlinApp(App):
    """A simple reproduction of one game on the Merlin hand held console."""

    CSS = """
    Screen {
        align: center middle;
    }

    Screen.-win {
        background: transparent;
    }

    Screen.-win Timer {
        color: $success;
    }

    Grid {
        width: auto;
        height: auto;
        border: thick $border;
        padding: 1 2;
        grid-size: 3 3;
        grid-rows: auto;
        grid-columns: auto;
        grid-gutter: 1 1;
        background: $surface;
    }
    """

    def render(self) -> LinearGradient:
        """Renders a gradient, when the background is transparent."""
        stops = [(i / (len(COLORS) - 1), c) for i, c in enumerate(COLORS)]
        return LinearGradient(30.0, stops)

    def compose(self) -> ComposeResult:
        """Compose a timer, and a grid of 9 switches."""
        yield Timer()
        with Grid():
            for switch in (7, 8, 9, 4, 5, 6, 1, 2, 3):
                yield LabelSwitch(switch)

    def on_mount(self) -> None:
        """Randomize the switches on mount."""
        for switch_no in range(1, 10):
            if random.randint(0, 1):
                self.query_one(f"#switch-{switch_no}", Switch).toggle()

    def check_win(self) -> bool:
        """Check for a win."""
        on_switches = {
            int(switch.name or "0") for switch in self.query(Switch) if switch.value
        }
        return on_switches == {1, 2, 3, 4, 6, 7, 8, 9}

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Called when a switch is toggled."""
        # The switch that was pressed
        switch_no = int(event.switch.name or "0")
        # Also toggle corresponding switches
        with self.prevent(Switch.Changed):
            for toggle_no in TOGGLES[switch_no]:
                self.query_one(f"#switch-{toggle_no}", Switch).toggle()
        # Check the win
        if self.check_win():
            self.query_one("Screen").add_class("-win")
            self.query_one(Timer).running = False
            self.notify("You win!", title="congratulations", severity="information")

    def on_key(self, event: events.Key) -> None:
        """Maps switches to keys, so we can use the keyboard as well."""
        if event.character and event.character.isdigit():
            self.query_one(f"#switch-{event.character}", Switch).toggle()


if __name__ == "__main__":
    MerlinApp().run()
