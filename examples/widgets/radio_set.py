from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import RadioButton, RadioSet


class RadioChoicesApp(App[None]):
    CSS_PATH = "radio_set.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            # A RadioSet built up from RadioButtons.
            with RadioSet(id="focus_me"):
                yield RadioButton("Battlestar Galactica")
                yield RadioButton("Dune 1984")
                yield RadioButton("Dune 2021")
                yield RadioButton("Serenity", value=True)
                yield RadioButton("Star Trek: The Motion Picture")
                yield RadioButton("Star Wars: A New Hope")
                yield RadioButton("The Last Starfighter")
                yield RadioButton(
                    Text.from_markup(
                        "Total Recall :backhand_index_pointing_right: :red_circle:"
                    )
                )
                yield RadioButton("Wing Commander")
            # A RadioSet built up from a collection of strings.
            yield RadioSet(
                "Amanda",
                "Connor MacLeod",
                "Duncan MacLeod",
                "Heather MacLeod",
                "Joe Dawson",
                "Kurgan, [bold italic red]The[/]",
                "Methos",
                "Rachel Ellenstein",
                "Ramírez",
            )

    def on_mount(self) -> None:
        self.query_one("#focus_me").focus()


if __name__ == "__main__":
    RadioChoicesApp().run()
