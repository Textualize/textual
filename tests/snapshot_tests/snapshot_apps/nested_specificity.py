from textual.app import App, ComposeResult
from textual.widgets import Static


class BaseTester(Static, can_focus=True):
    DEFAULT_CSS = """
    BaseTester:focus {
        background: yellow;
        border: thick magenta;
    }
    """


class NonNestedCSS(BaseTester):
    DEFAULT_CSS = """
    NonNestedCSS {
        width: 1fr;
        height: 1fr;
        background: red 10%;
        border: blank;
    }

    NonNestedCSS:focus {
        background: red 20%;
        border: round red;
    }
    """


class NestedCSS(BaseTester):
    DEFAULT_CSS = """
    NestedCSS {
        width: 1fr;
        height: 1fr;        

        &:focus {
            background: green 20%;
            border: round green;
        }

        background: green 10%;
        border: blank;
    }
    """


class NestedPseudoClassesApp(App[None]):
    AUTO_FOCUS = "NestedCSS"

    CSS = """
    Screen {
        layout: horizontal;
    }
    """

    def compose(self) -> ComposeResult:
        yield NonNestedCSS("This isn't using nested CSS")
        yield NestedCSS("This is using nested CSS")


if __name__ == "__main__":
    NestedPseudoClassesApp().run()
