from rich.console import RenderableType
from rich.text import Text
import rich.repr

from .. import events
from ..widget import Widget


@rich.repr.auto
class Footer(Widget):
    def __init__(self) -> None:
        self.keys: list[tuple[str, str]] = []
        super().__init__()
        self.layout_size = 1

    def __rich_repr__(self) -> rich.repr.RichReprResult:
        yield "footer"

    def add_key(self, key: str, label: str) -> None:
        self.keys.append((key, label))

    def render(self) -> RenderableType:

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
