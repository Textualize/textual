from textual.app import App, Screen, ComposeResult
from textual.widgets import Static, Footer, Pretty


class ModalScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Pretty(self.app.screen_stack)
        yield Footer()

    def on_screen_resume(self):
        self.query_one(Pretty).update(self.app.screen_stack)


class NewScreen(Screen):
    def compose(self):
        yield Pretty(self.app.screen_stack)
        yield Footer()

    def on_screen_resume(self):
        self.query_one(Pretty).update(self.app.screen_stack)


class ScreenApp(App):
    DEFAULT_CSS = """
    ScreenApp Screen {
        background: #111144;
        color: white;
     
       
    }
    ScreenApp ModalScreen {
        background: #114411;
        color: white;
        
      
    }
    ScreenApp Pretty {        
        height: auto;        
        content-align: center middle;
        background: white 20%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("On Screen 1")
        yield Footer()

    def on_mount(self) -> None:

        self.install_screen(NewScreen("Screen1"), name="1")
        self.install_screen(NewScreen("Screen2"), name="2")
        self.install_screen(NewScreen("Screen3"), name="3")

        self.bind("1", "switch_screen('1')", description="Screen 1")
        self.bind("2", "switch_screen('2')", description="Screen 2")
        self.bind("3", "switch_screen('3')", description="Screen 3")
        self.bind("s", "modal_screen", description="add screen")
        self.bind("escape", "back", description="Go back")

    def action_modal_screen(self) -> None:
        self.push_screen(ModalScreen())


app = ScreenApp()
if __name__ == "__main__":
    app.run()
