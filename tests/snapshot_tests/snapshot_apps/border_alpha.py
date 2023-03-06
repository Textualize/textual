from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widget import Widget

class BorderAlphaApp(App[None]):

    CSS = """
    Grid { grid-size: 2 5; }

    #b0 { border: solid 0%; }
    #b1 { border: solid 10%; }
    #b2 { border: solid 20%; }
    #b3 { border: solid 30%; }
    #b4 { border: solid 40%; }
    #b5 { border: solid 50%; }
    #b6 { border: solid 60%; }
    #b7 { border: solid 70%; }
    #b8 { border: solid 80%; }
    #b9 { border: solid 90%; }
    """

    def compose( self ) -> ComposeResult:
        with Grid():
            for n in range(10):
                yield Widget(id=f"b{n}")

if __name__ == "__main__":
    BorderAlphaApp().run()
