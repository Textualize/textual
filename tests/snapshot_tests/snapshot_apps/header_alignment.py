from textual.app import App, ComposeResult  # Add ComposeResult
from textual.widgets import Header

class HeaderAlignmentApp(App):
    TITLE = "Title"
    SUB_TITLE = "Subtitle"

    def compose(self) -> ComposeResult:  # Add return type
        yield Header()

if __name__ == "__main__":
    HeaderAlignmentApp().run()