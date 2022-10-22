from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static


ERROR_TEXT = """
An error has occurred. To continue:

Press Enter to return to Windows, or

Press CTRL+ALT+DEL to restart your computer. If you do this,
you will lose any unsaved information in all open applications.

Error: 0E : 016F : BFF9B3D4
"""


class BSOD(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static(ERROR_TEXT)
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


class BSODApp(App):
    CSS_PATH = "screen01.css"
    SCREENS = {"bsod": BSOD()}
    BINDINGS = [("b", "push_screen('bsod')", "BSOD")]


if __name__ == "__main__":
    app = BSODApp()
    app.run()
