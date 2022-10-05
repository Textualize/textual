from textual.app import App, ComposeResult
from textual.widgets import Static


class GridLayoutExample(App):
    CSS_PATH = "grid_layout6_row_span.css"

    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two [b](column-span: 2 and row-span: 2)", classes="box", id="two")
        yield Static("Three", classes="box")
        yield Static("Four", classes="box")
        yield Static("Five", classes="box")
        yield Static("Six", classes="box")


app = GridLayoutExample()
if __name__ == "__main__":
    app.run()
