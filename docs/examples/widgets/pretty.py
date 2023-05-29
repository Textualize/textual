from textual.app import App, ComposeResult
from textual.widgets import Pretty

DATA = {
    "title": "Back to the Future",
    "releaseYear": 1985,
    "director": "Robert Zemeckis",
    "genre": "Adventure, Comedy, Sci-Fi",
    "cast": [
        {"actor": "Michael J. Fox", "character": "Marty McFly"},
        {"actor": "Christopher Lloyd", "character": "Dr. Emmett Brown"},
    ],
}


class PrettyExample(App):
    def compose(self) -> ComposeResult:
        yield Pretty(DATA)


app = PrettyExample()

if __name__ == "__main__":
    app.run()
