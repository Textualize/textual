from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import RadioButton, RadioSet


class RadioChoicesApp(App[None]):
    CSS_PATH = "radio_button.tcss"

    def compose(self) -> ComposeResult:
        with RadioSet():
            yield RadioButton("Battlestar Galactica")
            yield RadioButton("Dune 1984")
            yield RadioButton("Dune 2021", id="focus_me")
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

    def on_mount(self) -> None:
        self.query_one(RadioSet).focus()


if __name__ == "__main__":
    RadioChoicesApp().run()
