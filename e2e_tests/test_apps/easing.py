from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Placeholder


class EasingApp(App):
    CSS = """
    Placeholder {
        offset: 0 0;
        transition: offset 500ms linear;
    }
    Placeholder.with-margin {
        offset: 0 50%;
        background: navy;
    }
    """

    def on_load(self):
        """Bind keys here."""
        self.bind("q", "quit")

    def compose(self) -> ComposeResult:
        """Build layout here."""
        yield Placeholder(name="Moving!", id="moving_placeholder")

    def on_mount(self):
        self.set_timer(0.3, self.action_animate_placeholder)

    def action_animate_placeholder(self):
        self.get_child("moving_placeholder").add_class("with-margin")
        self.update_styles()


EasingApp(log=Path(__file__).parent / "easing.log").run()
