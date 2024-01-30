from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList
from textual.widgets.option_list import Option, Separator


class OptionListApp(App[None]):
    CSS_PATH = "option_list.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(
            Option("Aerilon", id="aer"),
            Option("Aquaria", id="aqu"),
            Separator(),
            Option("Canceron", id="can"),
            Option("Caprica", id="cap", disabled=True),
            Separator(),
            Option("Gemenon", id="gem"),
            Separator(),
            Option("Leonis", id="leo"),
            Option("Libran", id="lib"),
            Separator(),
            Option("Picon", id="pic"),
            Separator(),
            Option("Sagittaron", id="sag"),
            Option("Scorpia", id="sco"),
            Separator(),
            Option("Tauron", id="tau"),
            Separator(),
            Option("Virgon", id="vir"),
        )
        yield Footer()


if __name__ == "__main__":
    OptionListApp().run()
