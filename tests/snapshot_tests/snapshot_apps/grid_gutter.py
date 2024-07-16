from rich.markdown import Markdown
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Label, TabbedContent, TabPane


class FooApp(App):
    TITLE = "Demonstrator"

    CSS = """
        Screen {
            align: center middle;
        }
        
        #root {
            width: 60;
            height: 20;
            border: solid $accent;
        }
        .info-container {
            grid-rows: auto;
        }
        .value {
            padding: 0 2;
            border: tall $background;
        }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="root"):
            with TabbedContent():
                with TabPane("Information"):
                    with Grid(classes="info-container"):
                        yield Label(Markdown(long_text()), classes="value")


def long_text() -> str:
    return 'aaa naa aaaaa aaa aaaan, aaa\naaa, aaaa?", aa aaa aaaaanaaa *anaaaaaaana* aaaaaaaa aaaaaana aaa aaaaa aa\naaa, aa *aaaaaaaaa* aaa aaaa, "aaaa, an *aaaa* aaa aaaa, a aa". "aaaa, naa\naaaaaaaaaaa, aaa a aaaa aaaaaanaa aaaa aa a aaa!", aaa anaaaa, aaaaa\naaaaaaaa aanaaaaa. "Na! aaa naa. aaaaa. aa aaaaa naa. aaaaa aa na aaa.",\naaa aaaaaaaa aaaanaaaaa DONE.\n'


if __name__ == "__main__":
    FooApp().run()
