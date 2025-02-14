import pytest
from rich.segment import Segment
from rich.style import Style as RichStyle
from rich.text import Text

from textual._border import render_border_label, render_row
from textual.content import Content
from textual.style import Style
from textual.widget import Widget


def test_border_render_row():
    style = RichStyle.parse("red")
    row = (Segment("┏", style), Segment("━", style), Segment("┓", style))

    assert list(render_row(row, 5, False, False, ())) == [
        Segment(row[1].text * 5, row[1].style)
    ]
    assert list(render_row(row, 5, True, False, ())) == [
        row[0],
        Segment(row[1].text * 4, row[1].style),
    ]
    assert list(render_row(row, 5, False, True, ())) == [
        Segment(row[1].text * 4, row[1].style),
        row[2],
    ]
    assert list(render_row(row, 5, True, True, ())) == [
        row[0],
        Segment(row[1].text * 3, row[1].style),
        row[2],
    ]


def test_border_title_single_line():
    """The border_title gets set to a single line even when multiple lines are provided."""
    widget = Widget()

    assert widget.border_title is None

    widget.border_title = None
    assert widget.border_title is None

    widget.border_title = ""
    assert widget.border_title == ""

    widget.border_title = "How is life\ngoing for you?"
    assert widget.border_title == "How is life"

    widget.border_title = "How is life\n\rgoing for you?"
    assert widget.border_title == "How is life"

    widget.border_title = "Sorry you \r\n have to \n read this."
    assert widget.border_title == "Sorry you "

    widget.border_title = "[red]This also \n works with markup \n involved.[/]"
    assert widget.border_title == "[red]This also [/red]"

    widget.border_title = Text.from_markup("[bold]Hello World")
    assert widget.border_title == "[bold]Hello World[/bold]"


def test_border_subtitle_single_line():
    """The border_subtitle gets set to a single line even when multiple lines are provided."""
    widget = Widget()

    widget.border_subtitle = ""
    assert widget.border_subtitle == ""

    widget.border_subtitle = "How is life\ngoing for you?"
    assert widget.border_subtitle == "How is life"

    widget.border_subtitle = "How is life\n\rgoing for you?"
    assert widget.border_subtitle == "How is life"

    widget.border_subtitle = "Sorry you \r\n have to \n read this."
    assert widget.border_subtitle == "Sorry you "

    widget.border_subtitle = "[red]This also \n works with markup \n involved.[/]"
    assert widget.border_subtitle == "[red]This also [/red]"

    widget.border_subtitle = Text.from_markup("[bold]Hello World")
    assert widget.border_subtitle == "[bold]Hello World[/bold]"


@pytest.mark.parametrize(
    ["width", "has_left_corner", "has_right_corner"],
    [
        (10, True, True),
        (10, True, False),
        (10, False, False),
        (10, False, True),
        (1, True, True),
        (1, True, False),
        (1, False, False),
        (1, False, True),
    ],
)
def test_render_border_label_empty_label_skipped(
    width: int, has_left_corner: bool, has_right_corner: bool
):
    """Test that we get an empty list of segments if there is no label to display."""

    assert [] == list(
        render_border_label(
            (Content(""), Style()),
            True,
            "round",
            width,
            Style(),
            Style(),
            Style(),
            has_left_corner,
            has_right_corner,
        )
    )


@pytest.mark.parametrize(
    ["label", "width", "has_left_corner", "has_right_corner"],
    [
        ("hey", 2, True, True),
        ("hey", 2, True, False),
        ("hey", 2, False, True),
        ("hey", 3, True, True),
        ("hey", 4, True, True),
    ],
)
def test_render_border_label_skipped_if_narrow(
    label: str, width: int, has_left_corner: bool, has_right_corner: bool
):
    """Test that we skip rendering a label when we do not have space for it.

    In order for us to have enough space for the label, we need to have space for the
    corners that we need (none, just one, or both) and we need to be able to have two
    blank spaces around the label (one on each side).
    If we don't have space for all of these, we skip the label altogether.
    """

    assert [] == list(
        render_border_label(
            (Content.from_markup(label), Style()),
            True,
            "round",
            width,
            Style(),
            Style(),
            Style(),
            has_left_corner,
            has_right_corner,
        )
    )


@pytest.mark.parametrize(
    "label",
    [
        "Why did the scarecrow",
        "win a Nobel prize?",
        "because it was outstanding",
        "in its field.",
    ],
)
def test_render_border_label_wide_plain(label: str):
    """Test label rendering in a wide area with no styling."""

    BIG_NUM = 9999
    args = (
        True,
        "round",
        BIG_NUM,
        Style(),
        Style(),
        Style(),
        True,
        True,
    )
    segments = render_border_label((Content.from_markup(label), Style()), *args)
    (segment,) = segments

    assert segment == Segment(f" {label} ", None)


@pytest.mark.parametrize(
    "label",
    [
        "[b][/]",
        "[i b][/]",
        "[white on red][/]",
        "[blue]",
    ],
)
def test_render_border_empty_text_with_markup(label: str):
    """Test label rendering if there is no text but some markup."""
    assert [] == list(
        render_border_label(
            (Content.from_markup(label), Style()),
            True,
            "round",
            999,
            Style(),
            Style(),
            Style(),
            True,
            True,
        )
    )


def test_render_border_label():
    """Test label rendering with styling, with and without overflow."""

    label = "[b][on red]What [i]is up[/on red] with you?[/]"
    border_style = Style.parse("green on blue")

    # Implicit test on the number of segments returned:
    segments = list(
        render_border_label(
            (Content.from_markup(label), Style.null()),
            True,
            "round",
            9999,
            Style(),
            Style(),
            border_style,
            True,
            True,
        )
    )

    for segment in segments:
        print("!!", segment)

    blank1, what, is_up, with_you, blank2 = segments

    expected_blank = Segment(" ", border_style.rich_style)
    assert blank1 == expected_blank
    assert blank2 == expected_blank

    what_style = Style.parse("b on red")
    expected_what = Segment("What ", (border_style + what_style).rich_style)
    print(what)
    print(expected_what)
    assert what == expected_what

    is_up_style = Style.parse("b on red i")
    expected_is_up = Segment("is up", (border_style + is_up_style).rich_style)
    assert is_up == expected_is_up

    with_you_style = Style.parse("b i")
    expected_with_you = Segment(
        " with you?", (border_style + with_you_style).rich_style
    )
    assert with_you == expected_with_you

    blank1, what, blank2 = render_border_label(
        (Content.from_markup(label), Style()),
        True,
        "round",
        5 + 4,  # 5 where "What…" fits + 2 for the blank spaces + 2 for the corners.
        Style(),
        Style(),
        border_style,
        True,  # This corner costs 2 cells.
        True,  # This corner costs 2 cells.
    )

    assert blank1 == expected_blank
    assert blank2 == expected_blank

    expected_what = Segment("What…", (border_style + what_style).rich_style)
    assert what == expected_what
