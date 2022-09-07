from textual.app import App
from textual.widgets import TextInput


class InputApp(App):

    CSS = """
    TextInput {
       
    }
    """

    def compose(self):
        yield TextInput(initial="foo")


app = InputApp()
