from __future__ import annotations

from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):

    BINDINGS = [("a", "add", "add")]

    def compose( self ) -> ComposeResult:
        with Horizontal():
            yield OptionList(
                "One",
                Option("Two"),
                None,
                Text.from_markup("[red]Three[/]")
            )
            yield OptionList(id="later-individual")
            yield OptionList(id="later-at-once")
            yield OptionList(id="after-mount")

    def on_mount(self) -> None:
        options: list[None | str | Text | Option] = [
            "One",
            Option("Two"),
            None,
            Text.from_markup("[red]Three[/]"),
        ]
        option_list = self.query_one("#later-individual", OptionList)
        for option in options:
            option_list.add_option(option)
        option_list.highlighted = 0
        option_list = self.query_one("#later-at-once", OptionList)
        option_list.add_options([
            "One",
            Option("Two"),
            None,
            Text.from_markup("[red]Three[/]"),
        ])
        option_list.highlighted = 0

    def action_add(self):
        option_list = self.query_one("#after-mount", OptionList)
        option_list.add_options([
            "One",
            Option("Two"),
            None,
            Text.from_markup("[red]Three[/]"),
        ])
        option_list.highlighted = 0

if __name__ == "__main__":
    OptionListApp().run()
