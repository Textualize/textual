from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
import rich.repr

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
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(
                (f" {key_display} ", "default on default"), f" {binding.description} "
            )
            key_text.stylize(Style(meta={"@click": f"app.press('{binding.key}')"}))
            text.append_text(key_text)
            # text.append(f" {key_display} ", style="default on default")
            # text.append(f" {binding.description} ")

        # text.stylize(Style(meta={"@enter": "app.bell()"}))
        return text
