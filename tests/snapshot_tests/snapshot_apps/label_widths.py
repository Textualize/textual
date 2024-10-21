from textual.app import App
from textual.widgets import Label, Static
from rich.panel import Panel


class LabelWrap(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #l_data {
        border: blank;
        background: lightgray;
    }

    #s_data {
        border: blank;
        background: lightgreen;
    }

    #p_data {
        border: blank;
        background: lightgray;
    }
    """

    def __init__(self):
        super().__init__()

        self.data = (
            "Apple Banana Cherry Mango Fig Guava Pineapple:"
            "Dragon Unicorn Centaur Phoenix Chimera Castle"
        )

    def compose(self):
        yield Label(self.data, id="l_data")
        yield Static(self.data, id="s_data")
        yield Label(Panel(self.data), id="p_data")

    def on_mount(self):
        self.theme = "textual-light"


if __name__ == "__main__":
    app = LabelWrap()
    app.run()
