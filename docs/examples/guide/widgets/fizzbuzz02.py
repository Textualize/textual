from rich.table import Table

from textual.app import App, ComposeResult
from textual.geometry import Size
from textual.widgets import Static


class FizzBuzz(Static):
    def on_mount(self) -> None:
        table = Table("Number", "Fizz?", "Buzz?", expand=True)
        for n in range(1, 16):
            fizz = not n % 3
            buzz = not n % 5
            table.add_row(
                str(n),
                "fizz" if fizz else "",
                "buzz" if buzz else "",
            )
        self.update(table)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Force content width size."""
        return 50


class FizzBuzzApp(App):
    CSS_PATH = "fizzbuzz02.css"

    def compose(self) -> ComposeResult:
        yield FizzBuzz()


if __name__ == "__main__":
    app = FizzBuzzApp()
    app.run()
