from textual.app import App

from textual.layout import Container
from textual.widgets import Button, Static


class CalculatorApp(App):
    def compose(self):
        yield Container(
            Static("0", classes="display"),
            Button("AC", classes="special"),
            Button("+/-", classes="special"),
            Button("%", classes="special"),
            Button("÷", variant="warning"),
            Button("7"),
            Button("8"),
            Button("9"),
            Button("×", variant="warning"),
            Button("4"),
            Button("5"),
            Button("6"),
            Button("-", variant="warning"),
            Button("1"),
            Button("2"),
            Button("3"),
            Button("+", variant="warning"),
            Button("0", classes="operator zero"),
            Button("."),
            Button("=", variant="warning"),
            id="calculator",
        )
        self.dark = True


app = CalculatorApp(css_path="calculator.css")
if __name__ == "__main__":
    app.run()
