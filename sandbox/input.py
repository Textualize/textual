from textual.app import App
from textual.widget import Widget

from textual.widgets.text_input import TextInput, TextWidgetBase, TextArea


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 1.8 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) / 1.8


class InputApp(App[str]):
    def on_mount(self) -> None:
        self.fahrenheit = TextInput(placeholder="Fahrenheit", id="fahrenheit")
        self.celsius = TextInput(placeholder="Celsius", id="celsius")
        self.fahrenheit.focus()
        text_boxes = Widget(self.fahrenheit, self.celsius)
        self.mount(inputs=text_boxes)
        self.mount(spacer=Widget())
        self.mount(footer=TextInput(placeholder="Footer Search Bar"))
        self.mount(text_area=TextArea())

    def handle_changed(self, event: TextWidgetBase.Changed) -> None:
        try:
            value = float(event.value)
        except ValueError:
            return
        if event.sender == self.celsius:
            fahrenheit = celsius_to_fahrenheit(value)
            self.fahrenheit.current_text = f"{fahrenheit:.1f}"
        elif event.sender == self.fahrenheit:
            celsius = fahrenheit_to_celsius(value)
            self.celsius.current_text = f"{celsius:.1f}"


app = InputApp(
    log_path="textual.log", css_path="input.scss", watch_css=True, log_verbosity=2
)

if __name__ == "__main__":
    result = app.run()
    print(repr(result))
