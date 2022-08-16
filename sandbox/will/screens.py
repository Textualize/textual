from textual.app import App, Screen, ComposeResult
from textual.widgets import Static, Footer, Pretty


class ModalScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Pretty(self.app.screen_stack)
        yield Footer()

    def on_screen_resume(self):
        self.query("*").refresh()


class NewScreen(Screen):
    def compose(self):
        yield Pretty(self.app.screen_stack)
        yield Footer()

    def on_screen_resume(self):
        self.query("*").refresh()


class ScreenApp(App):
    CSS = """
    ScreenApp Screen {
        background: #111144;
        color: white;
    }
    ScreenApp ModalScreen {
        background: #114411;
        color: white;
    }
    ScreenApp Static {
        height: 100%;        
        content-align: center middle;
    }
    """

    SCREENS = {
        "1": NewScreen("screen 1"),
        "2": NewScreen("screen 2"),
        "3": NewScreen("screen 3"),
    }

    def compose(self) -> ComposeResult:
        yield Static("On Screen 1")
        yield Footer()

    def on_mount(self) -> None:
        self.bind("1", "switch_screen('1')", description="Screen 1")
        self.bind("2", "switch_screen('2')", description="Screen 2")
        self.bind("3", "switch_screen('3')", description="Screen 3")
        self.bind("s", "modal_screen", description="add screen")
        self.bind("escape", "back", description="Go back")

    def action_modal_screen(self) -> None:
        self.push_screen(ModalScreen())


app = ScreenApp()
app.run()
