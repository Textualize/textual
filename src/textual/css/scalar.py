from __future__ import annotations

import re
from enum import Enum, unique
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, NamedTuple

import rich.repr

from ..geometry import Offset, Size, clamp


class ScalarError(Exception):
    """Base class for exceptions raised by the Scalar class."""


class ScalarResolveError(ScalarError):
    """Raised for errors resolving scalars (unlikely to occur in practice)."""


class ScalarParseError(ScalarError):
    """Raised when a scalar couldn't be parsed from a string."""


@unique
class Unit(Enum):
    """Enumeration of the various units inherited from CSS."""

    CELLS = 1
    FRACTION = 2
    PERCENT = 3
    WIDTH = 4
    HEIGHT = 5
    VIEW_WIDTH = 6
    VIEW_HEIGHT = 7
    AUTO = 8


UNIT_SYMBOL = {
    Unit.CELLS: "",
    Unit.FRACTION: "fr",
    Unit.PERCENT: "%",
    Unit.WIDTH: "w",
    Unit.HEIGHT: "h",
    Unit.VIEW_WIDTH: "vw",
    Unit.VIEW_HEIGHT: "vh",
}

SYMBOL_UNIT = {v: k for k, v in UNIT_SYMBOL.items()}

_MATCH_SCALAR = re.compile(r"^(-?\d+\.?\d*)(fr|%|w|h|vw|vh)?$").match


def _resolve_cells(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves explicit cell size, i.e. width: 10

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return Fraction(value)


def _resolve_fraction(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves a fraction unit i.e. width: 2fr

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return fraction_unit * Fraction(value)


def _resolve_width(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves width unit i.e. width: 50w.

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return Fraction(value) * Fraction(size.width, 100)


def _resolve_height(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves height unit, i.e. height: 12h.

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return Fraction(value) * Fraction(size.height, 100)


def _resolve_view_width(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves view width unit, i.e. width: 25vw.

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return Fraction(value) * Fraction(viewport.width, 100)


def _resolve_view_height(
    value: float, size: Size, viewport: Size, fraction_unit: Fraction
) -> Fraction:
    """Resolves view height unit, i.e. height: 25vh.

    Args:
        value: Scalar value.
        size: Size of widget.
        viewport: Size of viewport.
        fraction_unit: Size of fraction, i.e. size of 1fr as a Fraction.

    Returns:
        Resolved unit.
    """
    return Fraction(value) * Fraction(viewport.height, 100)


RESOLVE_MAP = {
    Unit.CELLS: _resolve_cells,
    Unit.FRACTION: _resolve_fraction,
    Unit.WIDTH: _resolve_width,
    Unit.HEIGHT: _resolve_height,
    Unit.VIEW_WIDTH: _resolve_view_width,
    Unit.VIEW_HEIGHT: _resolve_view_height,
}


def get_symbols(units: Iterable[Unit]) -> list[str]:
    """Get symbols for an iterable of units.

    Args:
        units: A number of units.

    Returns:
        List of symbols.
    """
    return [UNIT_SYMBOL[unit] for unit in units]


class Scalar(NamedTuple):
    """A numeric value and a unit."""

    value: float
    unit: Unit
    percent_unit: Unit

    def __str__(self) -> str:
        value, unit, _ = self
        if unit == Unit.AUTO:
            return "auto"
        return f"{int(value) if value.is_integer() else value}{self.symbol}"

    @property
    def is_cells(self) -> bool:
        """Check if the Scalar is explicit cells."""
        return self.unit == Unit.CELLS

    @property
    def is_percent(self) -> bool:
        """Check if the Scalar is a percentage unit."""
        return self.unit == Unit.PERCENT

    @property
    def is_fraction(self) -> bool:
        """Check if the unit is a fraction."""
        return self.unit == Unit.FRACTION

    @property
    def cells(self) -> int | None:
        """Check if the unit is explicit cells."""
        value, unit, _ = self
        return int(value) if unit == Unit.CELLS else None

    @property
    def fraction(self) -> int | None:
        """Get the fraction value, or None if not a value."""
        value, unit, _ = self
        return int(value) if unit == Unit.FRACTION else None

    @property
    def symbol(self) -> str:
        """Get the symbol of this unit."""
        return UNIT_SYMBOL[self.unit]

    @property
    def is_auto(self) -> bool:
        """Check if this is an auto unit."""
        return self.unit == Unit.AUTO

    @classmethod
    def from_number(cls, value: float) -> Scalar:
        """Create a scalar with cells unit.

        Args:
            value: A number of cells.

        Returns:
            New Scalar.
        """
        return cls(float(value), Unit.CELLS, Unit.WIDTH)

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(cls, token: str, percent_unit: Unit = Unit.WIDTH) -> Scalar:
        """Parse a string in to a Scalar

        Args:
            token: A string containing a scalar, e.g. "3.14fr"

        Raises:
            ScalarParseError: If the value is not a valid scalar

        Returns:
            New scalar
        """
        if token.lower() == "auto":
            scalar = cls(1.0, Unit.AUTO, Unit.AUTO)
        else:
            match = _MATCH_SCALAR(token)
            if match is None:
                raise ScalarParseError(f"{token!r} is not a valid scalar")
            value, unit_name = match.groups()
            scalar = cls(float(value), SYMBOL_UNIT[unit_name or ""], percent_unit)
        return scalar

    @lru_cache(maxsize=4096)
    def resolve(
        self, size: Size, viewport: Size, fraction_unit: Fraction | None = None
    ) -> Fraction:
        """Resolve scalar with units in to a dimensions.

        Args:
            size: Size of the container.
            viewport: Size of the viewport (typically terminal size)

        Raises:
            ScalarResolveError: If the unit is unknown.

        Returns:
            A size (in cells)
        """
        value, unit, percent_unit = self

        if unit == Unit.PERCENT:
            unit = percent_unit
        try:
            dimension = RESOLVE_MAP[unit](
                value, size, viewport, fraction_unit or Fraction(1)
            )
        except KeyError:
            raise ScalarResolveError(f"expected dimensions; found {str(self)!r}")
        return dimension

    def copy_with(
        self,
        value: float | None = None,
        unit: Unit | None = None,
        percent_unit: Unit | None = None,
    ) -> Scalar:
        """Get a copy of this Scalar, with values optionally modified

        Args:
            value: The new value, or None to keep the same value
            unit: The new unit, or None to keep the same unit
            percent_unit: The new percent_unit, or None to keep the same percent_unit
        """
        return Scalar(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            percent_unit if percent_unit is not None else self.percent_unit,
        )


@rich.repr.auto(angular=True)
class ScalarOffset(NamedTuple):
    """An Offset with two scalars, used to animate between to Scalars."""

    x: Scalar
    y: Scalar

    @classmethod
    def null(cls) -> ScalarOffset:
        """Get a null scalar offset (0, 0)."""
        return NULL_SCALAR

    @classmethod
    def from_offset(cls, offset: tuple[int, int]) -> ScalarOffset:
        """Create a Scalar offset from a tuple of integers.

        Args:
            offset: Offset in cells.

        Returns:
            New offset.
        """
        x, y = offset
        return cls(
            Scalar(x, Unit.CELLS, Unit.WIDTH),
            Scalar(y, Unit.CELLS, Unit.HEIGHT),
        )

    def __bool__(self) -> bool:
        x, y = self
        return bool(x.value or y.value)

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, str(self.x)
        yield None, str(self.y)

    def resolve(self, size: Size, viewport: Size) -> Offset:
        """Resolve the offset in to cells.

        Args:
            size: Size of container.
            viewport: Size of viewport.

        Returns:
            Offset in cells.
        """
        x, y = self
        return Offset(
            round(x.resolve(size, viewport)),
            round(y.resolve(size, viewport)),
        )


NULL_SCALAR = ScalarOffset(Scalar.from_number(0), Scalar.from_number(0))


def percentage_string_to_float(string: str) -> float:
    """Convert a string percentage e.g. '20%' to a float e.g. 20.0.

    Args:
        string: The percentage string to convert.
    """
    string = string.strip()
    if string.endswith("%"):
        float_percentage = clamp(float(string[:-1]) / 100.0, 0.0, 1.0)
    else:
        float_percentage = float(string)
    return float_percentage
