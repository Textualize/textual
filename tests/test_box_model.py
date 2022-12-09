from __future__ import annotations

from fractions import Fraction

from textual.box_model import BoxModel, get_box_model
from textual.css.styles import Styles
from textual.geometry import Size, Spacing


def test_content_box():
    styles = Styles()
    styles.width = 10
    styles.height = 8
    styles.padding = 1
    styles.border = ("solid", "red")

    one = Fraction(1)

    # border-box is default
    assert styles.box_sizing == "border-box"

    def get_auto_width(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    def get_auto_height(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    # Size should be inclusive of padding / border
    assert box_model == BoxModel(Fraction(10), Fraction(8), Spacing(0, 0, 0, 0))

    # Switch to content-box
    styles.box_sizing = "content-box"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    # width and height have added padding / border to accommodate content
    assert box_model == BoxModel(Fraction(14), Fraction(12), Spacing(0, 0, 0, 0))


def test_width():
    """Test width settings."""
    styles = Styles()
    one = Fraction(1)

    def get_auto_width(container: Size, parent: Size) -> int:
        return 10

    def get_auto_height(container: Size, parent: Size, width: int) -> int:
        return 10

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(60), Fraction(20), Spacing(0, 0, 0, 0))

    # Add a margin and check that it is reported
    styles.margin = (1, 2, 3, 4)

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    # Set width to auto-detect
    styles.width = "auto"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    # Setting width to auto should call get_auto_width
    assert box_model == BoxModel(Fraction(10), Fraction(16), Spacing(1, 2, 3, 4))

    # Set width to 100 vw which should make it the width of the parent
    styles.width = "100vw"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(80), Fraction(16), Spacing(1, 2, 3, 4))

    # Set the width to 100% should make it fill the container size
    styles.width = "100%"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    styles.width = "100vw"
    styles.max_width = "50%"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(30), Fraction(16), Spacing(1, 2, 3, 4))


def test_height():
    """Test height settings."""
    styles = Styles()
    one = Fraction(1)

    def get_auto_width(container: Size, parent: Size) -> int:
        return 10

    def get_auto_height(container: Size, parent: Size, width: int) -> int:
        return 10

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(60), Fraction(20), Spacing(0, 0, 0, 0))

    # Add a margin and check that it is reported
    styles.margin = (1, 2, 3, 4)

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    # Set height to 100 vw which should make it the height of the parent
    styles.height = "100vh"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(24), Spacing(1, 2, 3, 4))

    # Set the height to 100% should make it fill the container size
    styles.height = "100%"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    styles.height = "auto"
    styles.margin = 2

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(56), Fraction(10), Spacing(2, 2, 2, 2))

    styles.margin = 1, 2, 3, 4
    styles.height = "100vh"
    styles.max_height = "50%"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(54), Fraction(10), Spacing(1, 2, 3, 4))

    # Set height to auto and set content height to 0 to check if box collapses.
    styles.height = "auto"

    box_model = get_box_model(
        styles, Size(60, 20), Size(80, 24), one, one, get_auto_width, lambda *_: 0
    )
    assert box_model == BoxModel(Fraction(54), Fraction(0), Spacing(1, 2, 3, 4))


def test_max():
    """Check that max_width and max_height are respected."""
    styles = Styles()
    styles.width = 100
    styles.height = 80
    styles.max_width = 40
    styles.max_height = 30
    one = Fraction(1)

    def get_auto_width(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    def get_auto_height(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    box_model = get_box_model(
        styles, Size(40, 30), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(40), Fraction(30), Spacing(0, 0, 0, 0))


def test_min():
    """Check that min_width and min_height are respected."""
    styles = Styles()
    styles.width = 10
    styles.height = 5
    styles.min_width = 40
    styles.min_height = 30
    one = Fraction(1)

    def get_auto_width(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    def get_auto_height(container: Size, parent: Size) -> int:
        assert False, "must not be called"

    box_model = get_box_model(
        styles, Size(40, 30), Size(80, 24), one, one, get_auto_width, get_auto_height
    )
    assert box_model == BoxModel(Fraction(40), Fraction(30), Spacing(0, 0, 0, 0))
