"""
Simulates a screenshot of the Textual devtools
"""

from textual_dev.renderables import DevConsoleHeader

from textual.app import App
from textual.widgets import Static


class ConsoleApp(App):
    def compose(self):
        self.dark = True
        yield Static(DevConsoleHeader())


app = ConsoleApp()
