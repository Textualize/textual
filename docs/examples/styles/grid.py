from textual.app import App
from textual.widgets import Static


class GridApp(App):
    def compose(self):
        yield Static("Grid cell 1\n\nrow-span: 3;\ncolumn-span: 2;", id="static1")
        yield Static("Grid cell 2", id="static2")
        yield Static("Grid cell 3", id="static3")
        yield Static("Grid cell 4", id="static4")
        yield Static("Grid cell 5", id="static5")
        yield Static("Grid cell 6", id="static6")
        yield Static("Grid cell 7", id="static7")


app = GridApp(css_path="grid.css")
