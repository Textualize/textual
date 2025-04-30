from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Footer, Markdown, Placeholder

HELP = """\
## Breakpoints

A demonstration of how to make an app respond to the dimensions of the terminal.

Try resizing the terminal, then have a look at the source to see how it works!

`ctrl+q` to quit.

"""


class BreakpointApp(App):

    HORIZONTAL_BREAKPOINTS = [
        (0, "-narrow"),
        (40, "-normal"),
        (80, "-wide"),
        (120, "-very-wide"),
    ]

    CSS = """
    Screen {
        overflow-y: auto;
        Placeholder { padding: 2; }
        Grid { grid-rows: auto; height: auto; }
        &.-narrow {
            Grid { grid-size: 1; }
        }
        &.-normal {
            Grid { grid-size: 2; }
        }
        &.-wide {
            Grid { grid-size: 4; }
        }
        &.-very-wide {
            Grid { grid-size: 6; }
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Markdown(HELP)
        with Grid():
            for n in range(16):
                yield Placeholder(f"Placeholder {n+1}")
        yield Footer()


if __name__ == "__main__":
    BreakpointApp().run()
