"""
Regression tests for #1406 https://github.com/Textualize/textual/issues/1406

The scalars in grid-rows and grid-columns were not aware of the dimension
they should be relative to.
"""

from textual.css.parse import parse_declarations
from textual.css.scalar import Unit
from textual.css.styles import Styles


def test_grid_rows_columns_relative_units_are_correct():
    """Ensure correct relative dimensions for programmatic assignments."""

    styles = Styles()

    styles.grid_columns = "1fr 5%"
    fr, percent = styles.grid_columns
    assert fr.percent_unit == Unit.WIDTH
    assert percent.percent_unit == Unit.WIDTH

    styles.grid_rows = "1fr 5%"
    fr, percent = styles.grid_rows
    assert fr.percent_unit == Unit.HEIGHT
    assert percent.percent_unit == Unit.HEIGHT


def test_styles_builder_uses_correct_relative_units_grid_rows_columns():
    """Ensure correct relative dimensions for CSS parsed from files."""

    CSS = "grid-rows: 1fr 5%; grid-columns: 1fr 5%;"

    styles = parse_declarations(CSS, "test")

    fr, percent = styles.grid_columns
    assert fr.percent_unit == Unit.WIDTH
    assert percent.percent_unit == Unit.WIDTH

    fr, percent = styles.grid_rows
    assert fr.percent_unit == Unit.HEIGHT
    assert percent.percent_unit == Unit.HEIGHT
