from textual.css.scalar import Scalar, Unit


def test_copy_with_value():
    old = Scalar(1, Unit.HEIGHT, Unit.CELLS)
    new = old.copy_with(value=2)
    assert new == Scalar(2, Unit.HEIGHT, Unit.CELLS)


def test_copy_with_unit():
    old = Scalar(1, Unit.HEIGHT, Unit.CELLS)
    new = old.copy_with(unit=Unit.WIDTH)
    assert new == Scalar(1, Unit.WIDTH, Unit.CELLS)


def test_copy_with_percent_unit():
    old = Scalar(1, Unit.HEIGHT, Unit.CELLS)
    new = old.copy_with(percent_unit=Unit.FRACTION)
    assert new == Scalar(1, Unit.HEIGHT, Unit.FRACTION)
