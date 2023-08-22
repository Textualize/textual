from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, RadioButton, RadioSet


class RadioSetChangedApp(App[None]):
    CSS_PATH = "radio_set_changed.tcss"

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            with Horizontal():
                with RadioSet(id="focus_me"):
                    yield RadioButton("Battlestar Galactica")
                    yield RadioButton("Dune 1984")
                    yield RadioButton("Dune 2021")
                    yield RadioButton("Serenity", value=True)
                    yield RadioButton("Star Trek: The Motion Picture")
                    yield RadioButton("Star Wars: A New Hope")
                    yield RadioButton("The Last Starfighter")
                    yield RadioButton(
                        "Total Recall :backhand_index_pointing_right: :red_circle:"
                    )
                    yield RadioButton("Wing Commander")
            with Horizontal():
                yield Label(id="pressed")
            with Horizontal():
                yield Label(id="index")

    def on_mount(self) -> None:
        self.query_one(RadioSet).focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.query_one("#pressed", Label).update(
            f"Pressed button label: {event.pressed.label}"
        )
        self.query_one("#index", Label).update(
            f"Pressed button index: {event.radio_set.pressed_index}"
        )


if __name__ == "__main__":
    RadioSetChangedApp().run()
