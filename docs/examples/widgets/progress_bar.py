from textual.app import App, ComposeResult
from textual.containers import Center, VerticalScroll
from textual.widgets import Button, Header, Input, Label, ProgressBar


class FundingProgressApp(App[None]):
    CSS_PATH = "progress_bar.tcss"

    TITLE = "Funding tracking"

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Label("Funding: ")
            yield ProgressBar(total=100, show_eta=False)  # (1)!
        with Center():
            yield Input(placeholder="$$$")
            yield Button("Donate")

        yield VerticalScroll(id="history")

    def on_button_pressed(self) -> None:
        self.add_donation()

    def on_input_submitted(self) -> None:
        self.add_donation()

    def add_donation(self) -> None:
        text_value = self.query_one(Input).value
        try:
            value = int(text_value)
        except ValueError:
            return
        self.query_one(ProgressBar).advance(value)
        self.query_one(VerticalScroll).mount(Label(f"Donation for ${value} received!"))
        self.query_one(Input).value = ""


if __name__ == "__main__":
    FundingProgressApp().run()
