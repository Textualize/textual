from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration. I will face my fear."""


class WrapApp(App):
    CSS_PATH = "text_wrap.tcss"

    def compose(self) -> ComposeResult:
        yield Static(TEXT, id="static1")
        yield Static(TEXT, id="static2")


if __name__ == "__main__":
    app = WrapApp()
    app.run()
