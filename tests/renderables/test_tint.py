import io

from rich.console import Console
from rich.segment import Segments
from rich.terminal_theme import DIMMED_MONOKAI
from rich.text import Text

from textual._ansi_theme import DEFAULT_TERMINAL_THEME
from textual.color import Color
from textual.renderables.tint import Tint


def test_tint():
    console = Console(file=io.StringIO(), force_terminal=True, color_system="truecolor")
    renderable = Text.from_markup("[#aabbcc on #112233]foo")
    segments = list(console.render(renderable))
    console.print(
        Segments(
            Tint.process_segments(
                segments=segments,
                color=Color(0, 100, 0, 0.5),
                ansi_theme=DEFAULT_TERMINAL_THEME,
            )
        )
    )
    output = console.file.getvalue()
    print(repr(output))
    expected = "\x1b[38;2;85;143;102;48;2;8;67;25mfoo\x1b[0m\n"
    assert output == expected


def test_tint_ansi_mapping():
    console = Console(file=io.StringIO(), force_terminal=True, color_system="truecolor")
    renderable = Text.from_markup("[red on yellow]foo")
    segments = list(console.render(renderable))
    console.print(
        Segments(
            Tint.process_segments(
                segments=segments,
                color=Color(0, 100, 0, 0.5),
                ansi_theme=DIMMED_MONOKAI,
            )
        )
    )
    output = console.file.getvalue()
    print(repr(output))
    expected = "\x1b[38;2;95;81;36;48;2;98;133;26mfoo\x1b[0m\n"
    assert output == expected
