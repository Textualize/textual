from __future__ import annotations

from rich.table import Table

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList

COLONIES: tuple[tuple[str, str, str, str], ...] = (
    ("Aerilon", "Demeter", "1.2 Billion", "Gaoth"),
    ("Aquaria", "Hermes", "75,000", "None"),
    ("Canceron", "Hephaestus", "6.7 Billion", "Hades"),
    ("Caprica", "Apollo", "4.9 Billion", "Caprica City"),
    ("Gemenon", "Hera", "2.8 Billion", "Oranu"),
    ("Leonis", "Artemis", "2.6 Billion", "Luminere"),
    ("Libran", "Athena", "2.1 Billion", "None"),
    ("Picon", "Poseidon", "1.4 Billion", "Queenstown"),
    ("Sagittaron", "Zeus", "1.7 Billion", "Tawa"),
    ("Scorpia", "Dionysus", "450 Million", "Celeste"),
    ("Tauron", "Ares", "2.5 Billion", "Hypatia"),
    ("Virgon", "Hestia", "4.3 Billion", "Boskirk"),
)


class OptionListApp(App[None]):
    CSS_PATH = "option_list.tcss"

    @staticmethod
    def colony(name: str, god: str, population: str, capital: str) -> Table:
        table = Table(title=f"Data for {name}", expand=True)
        table.add_column("Patron God")
        table.add_column("Population")
        table.add_column("Capital City")
        table.add_row(god, population, capital)
        return table

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(*[self.colony(*row) for row in COLONIES])
        yield Footer()


if __name__ == "__main__":
    OptionListApp().run()
