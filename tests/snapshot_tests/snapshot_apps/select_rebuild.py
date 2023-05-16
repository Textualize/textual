"""Test https://github.com/Textualize/textual/issues/2557"""

from textual.app import App, ComposeResult
from textual.widgets import Select, Button


class SelectRebuildApp(App[None]):

    def compose(self) -> ComposeResult:
        yield Select[int]((("1", 1), ("2", 2)))
        yield Button("Rebuild")

    def on_button_pressed(self):
        self.query_one(Select).set_options((
            ("This", 0), ("Should", 1), ("Be", 2),
            ("What", 3), ("Goes", 4), ("Into",5),
            ("The", 6), ("Snapshit", 7)
        ))

if __name__ == "__main__":
    SelectRebuildApp().run()
