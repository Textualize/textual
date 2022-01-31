from tests.utilities.render import render
from textual.renderables.underline_bar import UnderlineBar

MAGENTA = "\x1b[35;49m"
GREY = "\x1b[38;5;59;49m"
STOP = "\x1b[0m"


def test_no_highlight():
    bar = UnderlineBar(width=6)
    assert render(bar) == f"{GREY}━━━━━━{STOP}"


def test_highlight_from_zero():
    bar = UnderlineBar(highlight_range=(0, 2.5), width=6)
    assert render(bar) == (
        f"{MAGENTA}━━{STOP}{MAGENTA}╸{STOP}{GREY}━━━{STOP}"
    )


def test_highlight_from_zero_point_five():
    bar = UnderlineBar(highlight_range=(0.5, 2), width=6)
    assert render(bar) == (
        f"{MAGENTA}╺━{STOP}{GREY}╺{STOP}{GREY}━━━{STOP}"
    )


def test_highlight_middle():
    bar = UnderlineBar(highlight_range=(2, 4), width=6)
    assert render(bar) == (
        f"{GREY}━{STOP}"
        f"{GREY}╸{STOP}"
        f"{MAGENTA}━━{STOP}"
        f"{GREY}╺{STOP}"
        f"{GREY}━{STOP}"
    )


def test_highlight_half_start():
    bar = UnderlineBar(highlight_range=(2.5, 4), width=6)
    assert render(bar) == (
        f"{GREY}━━{STOP}"
        f"{MAGENTA}╺━{STOP}"
        f"{GREY}╺{STOP}"
        f"{GREY}━{STOP}"
    )


def test_highlight_half_end():
    bar = UnderlineBar(highlight_range=(2, 4.5), width=6)
    assert render(bar) == (
        f"{GREY}━{STOP}"
        f"{GREY}╸{STOP}"
        f"{MAGENTA}━━{STOP}"
        f"{MAGENTA}╸{STOP}"
        f"{GREY}━{STOP}"
    )


def test_highlight_half_start_and_half_end():
    bar = UnderlineBar(highlight_range=(2.5, 4.5), width=6)
    assert render(bar) == (
        f"{GREY}━━{STOP}"
        f"{MAGENTA}╺━{STOP}"
        f"{MAGENTA}╸{STOP}"
        f"{GREY}━{STOP}"
    )


def test_highlight_to_near_end():
    bar = UnderlineBar(highlight_range=(3, 5.5), width=6)
    assert render(bar) == (
        f"{GREY}━━{STOP}"
        f"{GREY}╸{STOP}"
        f"{MAGENTA}━━{STOP}"
        f"{MAGENTA}╸{STOP}"
    )


def test_highlight_to_end():
    bar = UnderlineBar(highlight_range=(3, 6), width=6)
    assert render(bar) == (
        f"{GREY}━━{STOP}{GREY}╸{STOP}{MAGENTA}━━━{STOP}"
    )


def test_highlight_out_of_bounds_start():
    bar = UnderlineBar(highlight_range=(-2, 3), width=6)
    assert render(bar) == (
        f"{MAGENTA}━━━{STOP}{GREY}╺{STOP}{GREY}━━{STOP}"
    )


def test_highlight_out_of_bounds_end():
    bar = UnderlineBar(highlight_range=(3, 9), width=6)
    assert render(bar) == (
        f"{GREY}━━{STOP}{GREY}╸{STOP}{MAGENTA}━━━{STOP}"
    )
