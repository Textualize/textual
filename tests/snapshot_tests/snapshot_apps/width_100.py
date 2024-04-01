from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Label


class Width100PCentApp(App[None]):

    CSS = """
    Vertical {
        border: solid red;
        width: auto;

        Label {
            border: solid green;
        }

        #first {
            width: 100%;
        }

        #second {
            width: auto;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("I want to be 100% of my parent", id="first")
            yield Label(
                "I want my parent to be wide enough to wrap me and no more", id="second"
            )


if __name__ == "__main__":
    Width100PCentApp().run()
