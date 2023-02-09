from rich.segment import Segment
from rich.style import Style

from textual._border import render_row


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
