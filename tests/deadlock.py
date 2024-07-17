"""
Called by test_pipe.py

"""

from textual.app import App
from textual.binding import Binding
from textual.widgets import Footer


class MyApp(App[None]):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def compose(self):
        yield Footer()


app = MyApp()
app.run()
