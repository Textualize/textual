import pytest

from textual.color import Color
from textual.style import Style


@pytest.mark.parametrize(
    ["markup", "style"],
    [
        ("", Style()),
        (
            "b",
            Style(bold=True),
        ),
        ("i", Style(italic=True)),
        ("u", Style(underline=True)),
        ("r", Style(reverse=True)),
        ("bold", Style(bold=True)),
        ("italic", Style(italic=True)),
        ("underline", Style(underline=True)),
        ("reverse", Style(reverse=True)),
        ("bold italic", Style(bold=True, italic=True)),
        ("not bold italic", Style(bold=False, italic=True)),
        ("bold not italic", Style(bold=True, italic=False)),
        ("rgb(10, 20, 30)", Style(foreground=Color(10, 20, 30))),
        ("rgba(10, 20, 30, 0.5)", Style(foreground=Color(10, 20, 30, 0.5))),
        ("rgb(10, 20, 30) 50%", Style(foreground=Color(10, 20, 30, 0.5))),
        ("on rgb(10, 20, 30)", Style(background=Color(10, 20, 30))),
        ("on rgb(10, 20, 30) 50%", Style(background=Color(10, 20, 30, 0.5))),
        ("@click=app.bell", Style.from_meta({"@click": "app.bell"})),
        ("@click='app.bell'", Style.from_meta({"@click": "app.bell"})),
        ('''@click="app.bell"''', Style.from_meta({"@click": "app.bell"})),
        ("@click=app.bell()", Style.from_meta({"@click": "app.bell()"})),
        (
            "@click=app.notify('hello')",
            Style.from_meta({"@click": "app.notify('hello')"}),
        ),
        (
            "@click=app.notify('hello [World]!')",
            Style.from_meta({"@click": "app.notify('hello [World]!')"}),
        ),
        (
            "@click=app.notify('hello') bold",
            Style(bold=True) + Style.from_meta({"@click": "app.notify('hello')"}),
        ),
    ],
)
def test_parse_style(markup: str, style: Style) -> None:
    """Check parsing of valid styles."""
    parsed_style = Style.parse(markup)
    print("parsed\t\t", repr(parsed_style))
    print("expected\t", repr(style))
    print(parsed_style.meta, style.meta)
    print(parsed_style._meta)
    print(style._meta)
    assert parsed_style == style
