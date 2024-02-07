from __future__ import annotations

from fractions import Fraction

from textual.box_model import BoxModel
from textual.geometry import Size, Spacing
from textual.widget import Widget


def test_content_box():
    one = Fraction(1)

    class TestWidget(Widget):
        def get_content_width(self, container: Size, parent: Size) -> int:
            assert False, "must not be called"

        def get_content_height(self, container: Size, parent: Size) -> int:
            assert False, "must not be called"

    widget = TestWidget()

    # border-box is default
    assert widget.styles.box_sizing == "border-box"

    widget.styles.width = 10
    widget.styles.height = 8
    widget.styles.padding = 1
    widget.styles.border = ("solid", "red")

    box_model = widget._get_box_model(
        Size(60, 20),
        Size(80, 24),
        one,
        one,
    )
    # Size should be inclusive of padding / border
    assert box_model == BoxModel(Fraction(10), Fraction(8), Spacing(0, 0, 0, 0))

    # Switch to content-box
    widget.styles.box_sizing = "content-box"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    # width and height have added padding / border to accommodate content
    assert box_model == BoxModel(Fraction(14), Fraction(12), Spacing(0, 0, 0, 0))


def test_width():
    """Test width settings."""

    one = Fraction(1)

    class TestWidget(Widget):
        def get_content_width(self, container: Size, parent: Size) -> int:
            return 10

        def get_content_height(self, container: Size, parent: Size, width: int) -> int:
            return 10

    widget = TestWidget()
    styles = widget.styles
    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(60), Fraction(20), Spacing(0, 0, 0, 0))

    # Add a margin and check that it is reported
    styles.margin = (1, 2, 3, 4)

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    # Set width to auto-detect
    styles.width = "auto"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    # Setting width to auto should call get_auto_width
    assert box_model == BoxModel(Fraction(10), Fraction(16), Spacing(1, 2, 3, 4))

    # Set width to 100 vw which should make it the width of the parent
    styles.width = "100vw"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(80), Fraction(16), Spacing(1, 2, 3, 4))

    # Set the width to 100% should make it fill the container size
    styles.width = "100%"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    styles.width = "100vw"
    styles.max_width = "50%"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(27), Fraction(16), Spacing(1, 2, 3, 4))


def test_height():
    """Test height settings."""

    one = Fraction(1)

    class TestWidget(Widget):
        def get_content_width(self, container: Size, parent: Size) -> int:
            return 10

        def get_content_height(self, container: Size, parent: Size, width: int) -> int:
            return 10

    widget = TestWidget()
    styles = widget.styles

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(60), Fraction(20), Spacing(0, 0, 0, 0))

    # Add a margin and check that it is reported
    styles.margin = (1, 2, 3, 4)

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    # Set height to 100 vw which should make it the height of the parent
    styles.height = "100vh"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(24), Spacing(1, 2, 3, 4))

    # Set the height to 100% should make it fill the container size
    styles.height = "100%"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(16), Spacing(1, 2, 3, 4))

    styles.height = "auto"
    styles.margin = 2

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    print(box_model)
    assert box_model == BoxModel(Fraction(56), Fraction(10), Spacing(2, 2, 2, 2))

    styles.margin = 1, 2, 3, 4
    styles.height = "100vh"
    styles.max_height = "50%"

    box_model = widget._get_box_model(Size(60, 20), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(54), Fraction(8), Spacing(1, 2, 3, 4))


def test_max():
    """Check that max_width and max_height are respected."""
    one = Fraction(1)

    class TestWidget(Widget):
        def get_content_width(self, container: Size, parent: Size) -> int:
            assert False, "must not be called"

        def get_content_height(self, container: Size, parent: Size, width: int) -> int:
            assert False, "must not be called"

    widget = TestWidget()
    styles = widget.styles

    styles.width = 100
    styles.height = 80
    styles.max_width = 40
    styles.max_height = 30

    box_model = widget._get_box_model(Size(40, 30), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(40), Fraction(30), Spacing(0, 0, 0, 0))


def test_min():
    """Check that min_width and min_height are respected."""

    one = Fraction(1)

    class TestWidget(Widget):
        def get_content_width(self, container: Size, parent: Size) -> int:
            assert False, "must not be called"

        def get_content_height(self, container: Size, parent: Size, width: int) -> int:
            assert False, "must not be called"

    widget = TestWidget()
    styles = widget.styles
    styles.width = 10
    styles.height = 5
    styles.min_width = 40
    styles.min_height = 30

    box_model = widget._get_box_model(Size(40, 30), Size(80, 24), one, one)
    assert box_model == BoxModel(Fraction(40), Fraction(30), Spacing(0, 0, 0, 0))
