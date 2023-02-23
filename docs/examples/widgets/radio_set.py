from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import RadioButton, RadioSet


class RadioChoicesApp(App[None]):
    CSS_PATH = "radio_set.css"

    def compose(self) -> ComposeResult:
        yield Horizontal(
            RadioSet(
                RadioButton("Battlestar Galactica"),
                RadioButton("Dune 1984"),
                RadioButton("Dune 2021"),
                RadioButton("Serenity", value=True),
                RadioButton("Star Trek: The Motion Picture"),
                RadioButton("Star Wars: A New Hope"),
                RadioButton("The Last Starfighter"),
                RadioButton(
                    "Total Recall :backhand_index_pointing_right: :red_circle:",
                    id="focus_me",
                ),
                RadioButton("Wing Commander"),
            ),
            RadioSet(
                "Amanda",
                "Connor MacLeod",
                "Duncan MacLeod",
                "Heather MacLeod",
                "Joe Dawson",
                "Kurgan, [bold italic red]The[/]",
                "Methos",
                "Rachel Ellenstein",
                "Ramírez",
            ),
        )

    def on_mount(self) -> None:
        self.query_one("#focus_me", RadioButton).focus()


if __name__ == "__main__":
    RadioChoicesApp().run()
