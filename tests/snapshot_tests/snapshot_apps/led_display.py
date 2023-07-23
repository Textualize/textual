import string
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.widgets import LedDisplay
from textual.widgets._led_display import _character_map


class MyApp(App):
    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield LedDisplay("EuroPython 2023", id="panel", allow_lower=True)

        yield Static("Digits: 0123456789")
        yield LedDisplay("0123456789")

        alphabet = "".join(k for k in _character_map)
        split_point = alphabet.index("z") + 1
        yield Static("Punctuation: " + alphabet[split_point:])
        yield LedDisplay(alphabet[split_point:])

        yield LedDisplay(string.ascii_uppercase)
        yield LedDisplay(string.ascii_lowercase, allow_lower=True)
        yield LedDisplay("The lazy fox jumps over the brown dog", allow_lower=True)

        yield Static("Chord notation:  C#m   Db min   F#7")
        yield LedDisplay("C#m   Db min   F#7", allow_lower=True)

        yield Static("Example using allow_lower=True, input=AbCdEf:")
        yield LedDisplay("AbCdEf", allow_lower=True)
        yield Static("Example using allow_lower=False (default), input=AbCdEf:")
        yield LedDisplay("AbCdEf", allow_lower=False)


if __name__ == "__main__":
    app = MyApp()
    app.run()
