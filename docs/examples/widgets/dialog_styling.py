from textual.app import App, ComposeResult
from textual.widgets import Button, Dialog, Label


class StyledDialogApp(App[None]):
    CSS_PATH = "dialog_styling.tcss"

    def compose(self) -> ComposeResult:
        with Dialog.error(title="Emergency Transmission"):
            yield Label(
                "This is the President of the United Federation of "
                "Planets. Do not approach the Earth. The transmissions of an "
                "orbiting probe are causing critical damage to this planet. "
                "It has almost totally ionized our atmosphere. All power "
                "sources have failed. All Earth-orbiting starships are "
                "powerless. The probe is vaporizing our oceans. We cannot "
                "survive unless a way can be found to respond to the probe. "
                "Further communications may not be possible. Save your "
                "energy."
            )
            with Dialog.ActionArea():
                yield Button("Obey")
                yield Button("Ignore")


if __name__ == "__main__":
    StyledDialogApp().run()
