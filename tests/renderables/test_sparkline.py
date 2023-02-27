from tests.utilities.render import render
from textual.renderables.sparkline import Sparkline

GREEN = "\x1b[38;2;0;255;0m"
RED = "\x1b[38;2;255;0;0m"
BLENDED = "\x1b[38;2;127;127;0m"  # Color between red and green
STOP = "\x1b[0m"


def test_sparkline_no_data():
    assert render(Sparkline([], width=4)) == f"{GREEN}▁▁▁▁{STOP}"


def test_sparkline_single_datapoint():
    assert render(Sparkline([2.5], width=4)) == f"{RED}████{STOP}"


def test_sparkline_two_values_min_max():
    assert render(Sparkline([2, 4], width=2)) == f"{GREEN}▁{STOP}{RED}█{STOP}"


def test_sparkline_expand_data_to_width():
    assert (
        render(Sparkline([2, 4], width=4))
        == f"{GREEN}▁{STOP}{GREEN}▁{STOP}{RED}█{STOP}{RED}█{STOP}"
    )


def test_sparkline_expand_data_to_width_non_divisible():
    assert (
        render(Sparkline([2, 4], width=3))
        == f"{GREEN}▁{STOP}{GREEN}▁{STOP}{RED}█{STOP}"
    )


def test_sparkline_shrink_data_to_width():
    assert (
        render(Sparkline([2, 2, 4, 4, 6, 6], width=3))
        == f"{GREEN}▁{STOP}{BLENDED}▄{STOP}{RED}█{STOP}"
    )


def test_sparkline_shrink_data_to_width_non_divisible():
    assert (
        render(Sparkline([1, 2, 3, 4, 5], width=3, summary_function=min))
        == f"{GREEN}▁{STOP}{BLENDED}▄{STOP}{RED}█{STOP}"
    )


def test_sparkline_color_blend():
    assert (
        render(Sparkline([1, 2, 3], width=3))
        == f"{GREEN}▁{STOP}{BLENDED}▄{STOP}{RED}█{STOP}"
    )
