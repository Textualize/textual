from rich.console import Console, ConsoleOptions, RenderableType
from rich.repr import rich_repr, RichReprResult
from rich.text import Text

from .. import events
from ..widget import Widget


class Footer(Widget):
    def __init__(self) -> None:
        self.keys: list[tuple[str, str]] = []
        super().__init__()

    def __rich_repr__(self) -> RichReprResult:
        yield "footer"

    def add_key(self, key: str, label: str) -> None:
        self.keys.append((key, label))

    def render(self, console: Console, options: ConsoleOptions) -> RenderableType:

        text = Text(
            style="white on dark_green",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for key, label in self.keys:
            text.append(f" {key.upper()} ", style="default on default")
            text.append(f" {label} ")
        return text
