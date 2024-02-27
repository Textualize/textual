from textual.app import App
from textual.screen import Screen
from textual.widgets import TextArea

TEXT = """\
foo
bar
baz
"""


class AltScreen(Screen[None]):
    def compose(self):
        yield TextArea(TEXT)


class TABug(App[None]):
    def on_mount(self):
        self.push_screen(AltScreen())


if __name__ == "__main__":
    app = TABug()
    app.run()
