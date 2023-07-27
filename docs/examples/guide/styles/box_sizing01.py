from textual.app import App, ComposeResult
from textual.widgets import Static


TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""


class BoxSizing(App):
    def compose(self) -> ComposeResult:
        self.widget1 = Static(TEXT)
        yield self.widget1
        self.widget2 = Static(TEXT)
        yield self.widget2

    def on_mount(self) -> None:
        self.widget1.styles.background = "purple"
        self.widget2.styles.background = "darkgreen"
        self.widget1.styles.width = 30
        self.widget2.styles.width = 30
        self.widget1.styles.height = 6
        self.widget2.styles.height = 6
        self.widget1.styles.border = ("heavy", "white")
        self.widget2.styles.border = ("heavy", "white")
        self.widget1.styles.padding = 1
        self.widget2.styles.padding = 1
        self.widget2.styles.box_sizing = "content-box"


if __name__ == "__main__":
    app = BoxSizing()
    app.run()
