from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea, Static, Button, Label


class InputVsTextArea(App[None]):
    CSS = """
    Screen > *, Screen > *:focus {
        width: 50%;
        height: 1fr;
        border: solid red;
    }
    App #ruler {
        width: 1fr;
        height: 1;
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("[reverse]0123456789[/]0123456789" * 4, id="ruler")

        input = Input()
        input.cursor_blink = False
        yield input

        text_area = TextArea()
        text_area.cursor_blink = False
        yield text_area

        yield Static()
        yield Button()


if __name__ == "__main__":
    InputVsTextArea().run()
