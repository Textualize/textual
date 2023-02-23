from textual.app import App, ComposeResult
from textual.widgets import RadioButton, RadioSet


class RadioChoicesApp(App[None]):
    CSS_PATH = "radio_button.css"

    def compose(self) -> ComposeResult:
        yield RadioSet(
            RadioButton("Battlestar Galactica"),
            RadioButton("Dune 1984"),
            RadioButton("Dune 2021", id="focus_me"),
            RadioButton("Serenity", value=True),
            RadioButton("Star Trek: The Motion Picture"),
            RadioButton("Star Wars: A New Hope"),
            RadioButton("The Last Starfighter"),
            RadioButton("Total Recall :backhand_index_pointing_right: :red_circle:"),
            RadioButton("Wing Commander"),
        )

    def on_mount(self) -> None:
        self.query_one("#focus_me", RadioButton).focus()


if __name__ == "__main__":
    RadioChoicesApp().run()
