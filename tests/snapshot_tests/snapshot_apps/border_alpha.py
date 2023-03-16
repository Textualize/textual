from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Label


class BorderAlphaApp(App[None]):
    CSS = """   
    .boxes {
        height: 3;
        width: 100%;
    }
    
    #box0 {
        border: heavy green 0%;
    }
    #box1 {
        border: heavy green 20%;
    }
    #box2 {
        border: heavy green 40%;
    }
    #box3 {
        border: heavy green 60%;
    }
    #box4 {
        border: heavy green 80%;
    }
    #box5 {
        border: heavy green 100%;
    }        
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            for box in range(6):
                yield Label(id=f"box{box}", classes="boxes")


if __name__ == "__main__":
    BorderAlphaApp().run()
