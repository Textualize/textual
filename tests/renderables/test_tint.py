import io

from rich.console import Console
from rich.text import Text

from textual.color import Color
from textual.renderables.tint import Tint


def test_tint():
    console = Console(file=io.StringIO(), force_terminal=True, color_system="truecolor")
    renderable = Text.from_markup("[#aabbcc on #112233]foo")
    console.print(Tint(renderable, Color(0, 100, 0, 0.5)))
    output = console.file.getvalue()
    print(repr(output))
    expected = "\x1b[38;2;85;143;102;48;2;8;67;25mfoo\x1b[0m\n"
    assert output == expected
