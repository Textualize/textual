from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    CSS_PATH = "option_list.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(
            Option("Aerilon", id="aer"),
            Option("Aquaria", id="aqu"),
            None,
            Option("Canceron", id="can"),
            Option("Caprica", id="cap", disabled=True),
            None,
            Option("Gemenon", id="gem"),
            None,
            Option("Leonis", id="leo"),
            Option("Libran", id="lib"),
            None,
            Option("Picon", id="pic"),
            None,
            Option("Sagittaron", id="sag"),
            Option("Scorpia", id="sco"),
            None,
            Option("Tauron", id="tau"),
            None,
            Option("Virgon", id="vir"),
        )
        yield Footer()


if __name__ == "__main__":
    OptionListApp().run()
