"""
Simulates a screenshot of the Textual devtools

"""

from textual.app import App

from textual.devtools.renderables import DevConsoleHeader
from textual.widgets import Static


class ConsoleApp(App):
    def compose(self):
        self.dark = True
        yield Static(DevConsoleHeader())


app = ConsoleApp()
