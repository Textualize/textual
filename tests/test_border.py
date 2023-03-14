from rich.segment import Segment
from rich.style import Style

from textual._border import render_row
from textual.widget import Widget


def test_border_render_row():
    style = Style.parse("red")
    row = (Segment("┏", style), Segment("━", style), Segment("┓", style))

    assert render_row(row, 5, False, False) == [Segment(row[1].text * 5, row[1].style)]
    assert render_row(row, 5, True, False) == [
        row[0],
        Segment(row[1].text * 4, row[1].style),
    ]
    assert render_row(row, 5, False, True) == [
        Segment(row[1].text * 4, row[1].style),
        row[2],
    ]
    assert render_row(row, 5, True, True) == [
        row[0],
        Segment(row[1].text * 3, row[1].style),
        row[2],
    ]


def test_border_title_single_line():
    """The border_title gets set to a single line even when multiple lines are provided."""
    widget = Widget()

    widget.border_title = ""
    assert widget.border_title == ""

    widget.border_title = "How is life\ngoing for you?"
    assert widget.border_title == "How is life"

    widget.border_title = "How is life\n\rgoing for you?"
    assert widget.border_title == "How is life"

    widget.border_title = "Sorry you \r\n have to \n read this."
    assert widget.border_title == "Sorry you "

    widget.border_title = "[red]This also \n works with markup \n involved.[/]"
    assert widget.border_title == "[red]This also "


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
    assert widget.border_subtitle == "[red]This also "
