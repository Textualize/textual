import pytest
from pytest import approx
from rich.console import Console
from rich.text import Text

from textual.app import App
from textual.color import Gradient
from textual.css.query import NoMatches
from textual.renderables.bar import _apply_gradient
from textual.widget import Widget
from textual.widgets import ProgressBar


def test_initial_status():
    pb = ProgressBar()
    assert pb.total is None
    assert pb.progress == 0
    assert pb.percentage is None

    pb = ProgressBar(total=100)
    assert pb.total == 100
    assert pb.progress == 0
    assert pb.percentage == 0


def test_advance():
    pb = ProgressBar(total=100)

    pb.advance(10)
    assert pb.progress == 10
    assert pb.percentage == approx(0.1)

    pb.advance(42)
    assert pb.progress == 52
    assert pb.percentage == approx(0.52)

    pb.advance(0.0625)
    assert pb.progress == 52.0625
    assert pb.percentage == approx(0.520625)


def test_advance_backwards():
    pb = ProgressBar(total=100)

    pb.progress = 50

    pb.advance(-10)
    assert pb.progress == 40


def test_progress_overflow():
    pb = ProgressBar(total=100)

    pb.advance(999_999)
    assert pb.percentage == 1

    pb.update(total=50)
    assert pb.percentage == 1


def test_progress_underflow():
    pb = ProgressBar(total=100)

    pb.advance(-999_999)
    assert pb.percentage == 0


def test_non_negative_total():
    pb = ProgressBar(total=-100)
    assert pb.total == 0


def test_update_total():
    pb = ProgressBar()

    pb.update(total=100)
    assert pb.total == 100

    pb.update(total=1000)
    assert pb.total == 1000

    pb.update(total=None)
    assert pb.total is None

    pb.update(total=100)
    assert pb.total == 100


def test_update_progress():
    pb = ProgressBar(total=100)

    pb.update(progress=10)
    assert pb.progress == 10

    pb.update(progress=73)
    assert pb.progress == 73

    pb.update(progress=40)
    assert pb.progress == 40


def test_update_advance():
    pb = ProgressBar(total=100)

    pb.update(advance=10)
    assert pb.progress == 10

    pb.update(advance=10)
    assert pb.progress == 20

    pb.update(advance=10)
    assert pb.progress == 30


def test_update():
    pb = ProgressBar()

    pb.update(total=100, progress=30, advance=20)
    assert pb.total == 100
    assert pb.progress == 50


def test_go_back_to_indeterminate():
    pb = ProgressBar()

    pb.total = 100
    assert pb.percentage == 0
    pb.total = None
    assert pb.percentage is None


@pytest.mark.parametrize(
    ["show_bar", "show_percentage", "show_eta"],
    [
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
async def test_show_sub_widgets(show_bar: bool, show_percentage: bool, show_eta: bool):
    class PBApp(App[None]):
        def compose(self):
            self.pb = ProgressBar(
                show_bar=show_bar, show_percentage=show_percentage, show_eta=show_eta
            )
            yield self.pb

    app = PBApp()

    async with app.run_test():
        if show_bar:
            bar = app.pb.query_one("#bar")
            assert isinstance(bar, Widget)
        else:
            with pytest.raises(NoMatches):
                app.pb.query_one("#bar")

        if show_percentage:
            percentage = app.pb.query_one("#percentage")
            assert isinstance(percentage, Widget)
        else:
            with pytest.raises(NoMatches):
                app.pb.query_one("#percentage")

        if show_eta:
            eta = app.pb.query_one("#eta")
            assert isinstance(eta, Widget)
        else:
            with pytest.raises(NoMatches):
                app.pb.query_one("#eta")


def test_apply_gradient():
    text = Text("foo")
    gradient = Gradient.from_colors("red", "blue")
    _apply_gradient(text, gradient, 1)
    console = Console()
    assert text.get_style_at_offset(console, 0).color.triplet == (255, 0, 0)
