from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList


class OptionListApp(App[None]):
    CSS_PATH = "option_list.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(
            "Aerilon",
            "Aquaria",
            "Canceron",
            "Caprica",
            "Gemenon",
            "Leonis",
            "Libran",
            "Picon",
            "Sagittaron",
            "Scorpia",
            "Tauron",
            "Virgon",
        )
        yield Footer()


if __name__ == "__main__":
    OptionListApp().run()
