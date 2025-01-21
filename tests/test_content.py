from rich.text import Text

from textual.content import Content, Span


def test_blank():
    """Check blank content."""
    blank = Content("")
    assert isinstance(blank, Content)
    assert str(blank) == ""
    assert blank.plain == ""
    assert not blank
    assert blank.markup == ""
    assert len(blank) == 0
    assert blank.spans == []


def test_simple():
    """Check content with simple unstyled text."""
    simple = Content("foo")
    assert isinstance(simple, Content)
    assert str(simple) == "foo"
    assert simple.plain == "foo"
    assert simple  # Not empty is truthy
    assert simple.markup == "foo"
    assert len(simple) == 3
    assert simple.spans == []


def test_constructor():
    content = Content("Hello, World")
    assert content
    assert len(content) == 12
    assert content.cell_length == 12
    assert content.plain == "Hello, World"
    repr(content)


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


def test_stylize() -> None:
    """Test the stylize method."""
    foo = Content("foo bar")
    assert foo.spans == []
    red_foo = foo.stylize("red")
    # stylize create a new object
    assert foo.spans == []
    # With no parameters, full string is stylized
    assert red_foo.spans == [Span(0, 7, "red")]
    red_foo = red_foo.stylize("blue", 4, 7)
    # Another span is appended
    assert red_foo.spans == [
        Span(0, 7, "red"),
        Span(4, 7, "blue"),
    ]


def test_stylize_before() -> None:
    """Test the stylize_before method."""
    foo = Content("foo bar")
    assert foo.spans == []
    red_foo = foo.stylize("red")
    # stylize create a new object
    assert foo.spans == []
    # With no parameters, full string is stylized
    assert red_foo.spans == [Span(0, 7, "red")]
    red_foo = red_foo.stylize_before("blue", 4, 7)
    # Another span is appended
    assert red_foo.spans == [
        Span(4, 7, "blue"),
        Span(0, 7, "red"),
    ]


def test_eq() -> None:
    assert Content("foo") == Content("foo")
    assert Content("foo") == "foo"
    assert Content("foo") != Content("bar")
    assert Content("foo") != "bar"


def test_add() -> None:
    # Simple cases
    assert Content("") + Content("") == Content("")
    assert Content("foo") + Content("") == Content("foo")
    # Works with simple strings
    assert Content("foo") + "" == Content("foo")
    assert "" + Content("foo") == Content("foo")

    # Test spans after addition
    content = Content.styled("foo", "red") + " " + Content.styled("bar", "blue")
    assert str(content) == "foo bar"
    assert content.spans == [Span(0, 3, "red"), Span(4, 7, "blue")]
    assert content.cell_length == 7


def test_from_markup():
    content = Content.from_markup("[red]Hello[/red] [blue]World[/blue]")
    assert len(content) == 11
    assert content.plain == "Hello World"
    assert content.spans == [
        Span(start=0, end=5, style="red"),
        Span(start=6, end=11, style="blue"),
    ]


def test_join():
    """Test the join method."""

    # Edge cases
    assert Content("").join([]) == ""
    assert Content(".").join([]) == ""
    assert Content("").join(["foo"]) == "foo"
    assert Content(".").join(["foo"]) == "foo"

    # Join strings and Content
    pieces = [Content.styled("foo", "red"), "bar", Content.styled("baz", "blue")]
    content = Content(".").join(pieces)
    assert content.plain == "foo.bar.baz"
    assert content.spans == [Span(0, 3, "red"), Span(8, 11, "blue")]
