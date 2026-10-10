from textual.app import App, ComposeResult
from textual.suggester import SuggestFromList
from textual.widgets import Input

# Values offered as completions as the user types.
COUNTRIES = [
    "England",
    "Scotland",
    "Portugal",
    "Spain",
    "France",
    "Germany",
    "Italy",
    "Greece",
]


class InputSuggestionsApp(App):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Country",
            suggester=SuggestFromList(COUNTRIES, case_sensitive=False),
        )


if __name__ == "__main__":
    app = InputSuggestionsApp()
    app.run()
