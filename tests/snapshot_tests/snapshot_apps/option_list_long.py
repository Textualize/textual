from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class LongOptionListApp(App[None]):
    def compose(self) -> ComposeResult:
        yield OptionList(*[Option(f"This is option #{n}") for n in range(100)])


if __name__ == "__main__":
    LongOptionListApp().run()
