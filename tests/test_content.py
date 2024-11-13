from rich.text import Text

from textual.content import Content, Span


def test_constructor():
    content = Content("Hello, World")
    assert content
    assert len(content) == 12
    assert content.cell_length == 12
    assert content.plain == "Hello, World"
    repr(content)
    assert content.align == "left"
    assert content.no_wrap is False
    assert content.ellipsis is False


def test_bool():
    assert bool(Content("foo")) is True
    assert bool(Content("")) is False


def test_from_rich_text():
    text = Text.from_markup("[red]Hello[/red] [blue]World[/blue]")
    content = Content.from_rich_text(text)
    assert len(content) == 11
    assert content.plain == "Hello World"
    assert [Span(start=0, end=5, style="red"), Span(start=6, end=11, style="blue")]


def test_styled():
    text = Content.styled("Hello", "red")
    assert text.plain == "Hello"
    assert len(text) == 5
    assert text.cell_length == 5
    assert text._spans == [Span(0, 5, "red")]


def test_getitem():
    content = Content("Hello, world").stylize("blue", 0, 5)
    assert content[0].plain == "H"
    assert content[0]._spans == [Span(0, 1, "blue")]
    assert content[-1].plain == "d"
    assert content[-1]._spans == []
    assert content[:2].plain == "He"
    assert content[:2]._spans == [Span(0, 2, "blue")]


def test_cell_length():
    assert Content("").cell_length == 0
    assert Content("foo").cell_length == 3
    assert Content("💩").cell_length == 2
