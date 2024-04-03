from textual.app import App, ComposeResult
from textual.widgets import Label, TabbedContent, TabPane


class ColorTabsApp(App):
    CSS = """
    TabbedContent #--content-tab-green {
        color: green;
    }

    TabbedContent #--content-tab-red {
        color: red;
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Red", id="red"):
                yield Label("Red!")
            with TabPane("Green", id="green"):
                yield Label("Green!")


if __name__ == "__main__":
    ColorTabsApp().run()
