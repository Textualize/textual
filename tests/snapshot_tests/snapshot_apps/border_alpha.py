from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widget import Widget

class BorderAlphaApp(App[None]):

    CSS = """
    Grid {
        height: 100%;
        width: 100%;
        grid-size: 2 2;
    }

    #b00 { border: 0%; }
    #b01 { border: 33%; }
    #b02 { border: 66%; }
    #b03 { border: 100%; }

    #b10 { border: solid 0%; }
    #b11 { border: dashed 33%; }
    #b12 { border: round 66%; }
    #b13 { border: ascii 100%; }

    #b20 { border: 0% red; }
    #b21 { border: 33% orange; }
    #b22 { border: 66% green; }
    #b23 { border: 100% blue; }

    #b30 { border: solid 0% red; }
    #b31 { border: dashed 33% orange; }
    #b32 { border: round 66% green; }
    #b33 { border: ascii 100% blue; }
    """

    def compose( self ) -> ComposeResult:
        with Grid():
            for outer in range(4):
                with Grid():
                    for inner in range(4):
                        yield Widget(id=f"b{outer}{inner}")

if __name__ == "__main__":
    BorderAlphaApp().run()
