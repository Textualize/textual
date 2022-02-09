import pytest
from rich.text import Text

from tests.utilities.render import render
from textual.renderables.opacity import Opacity


@pytest.mark.skip
def test_simple_opacity():
    text = Text("Hello, world!", style="#ff0000 on #00ff00")
    assert render(Opacity(text, value=.5)) == ""


@pytest.mark.skip
def test_ansi_colors_ignored():
    pass


@pytest.mark.skip
def test_opacity_no_style():
    pass


@pytest.mark.skip
def test_opacity_only_fg():
    pass


@pytest.mark.skip
def test_opacity_only_bg():
    pass
