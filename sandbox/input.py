from __future__ import annotations

from pathlib import Path

from textual.app import App
from textual.widget import Widget

from textual.widgets.text_input import TextInput, TextWidgetBase, TextArea


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 1.8 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) / 1.8


words = set(Path("/usr/share/dict/words").read_text().splitlines())


def word_autocompleter(value: str) -> str | None:
    # An example autocompleter that uses the Unix dictionary to suggest
    # word completions
    for word in words:
        if word.startswith(value):
            return word
    return None


class InputApp(App[str]):
    def on_mount(self) -> None:
        self.fahrenheit = TextInput(placeholder="Fahrenheit", id="fahrenheit")
        self.celsius = TextInput(placeholder="Celsius", id="celsius")
        self.fahrenheit.focus()
        text_boxes = Widget(self.fahrenheit, self.celsius)
        self.mount(inputs=text_boxes)
        self.mount(spacer=Widget())
        self.mount(
            top_search=Widget(
                TextInput(autocompleter=word_autocompleter, id="topsearchbox")
            )
        )
        self.mount(
            footer=TextInput(
                placeholder="Footer Search Bar", autocompleter=word_autocompleter
            )
        )
        self.mount(text_area=TextArea())

    def on_text_widget_base_changed(self, event: TextWidgetBase.Changed) -> None:
        try:
            value = float(event.value)
        except ValueError:
            return
        if event.sender == self.celsius:
            fahrenheit = celsius_to_fahrenheit(value)
            self.fahrenheit.value = f"{fahrenheit:.1f}"
        elif event.sender == self.fahrenheit:
            celsius = fahrenheit_to_celsius(value)
            self.celsius.value = f"{celsius:.1f}"


app = InputApp(log_path="textual.log", css_path="input.scss", watch_css=True)

if __name__ == "__main__":
    result = app.run()
