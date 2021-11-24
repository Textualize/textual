from __future__ import annotations

from enum import Enum, unique
import re
from typing import Iterable, NamedTuple


@unique
class Unit(Enum):
    CELLS = 1
    FRACTION = 2
    PERCENT = 3
    WIDTH = 4
    HEIGHT = 5
    VIEW_WIDTH = 6
    VIEW_HEIGHT = 7


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

_MATCH_SCALAR = re.compile(r"^(\d+\.?\d*)(fr|%|w|h|vw|vh)?$").match


def get_symbols(units: Iterable[Unit]) -> list[str]:
    """Get symbols for an iterable of units.

    Args:
        units (Iterable[Unit]): A number of units.

    Returns:
        list[str]: List of symbols.
    """
    return [UNIT_SYMBOL[unit] for unit in units]


class ScalarParseError(Exception):
    pass


class Scalar(NamedTuple):
    """A numeric value and a unit."""

    value: float
    unit: Unit

    def __str__(self) -> str:
        value, _unit = self
        return f"{int(value) if value.is_integer() else value}{self.symbol}"

    @property
    def cells(self) -> int | None:
        value, unit = self
        return int(value) if unit == Unit.CELLS else None

    @property
    def fraction(self) -> int | None:
        value, unit = self
        return int(value) if unit == Unit.FRACTION else None

    @property
    def symbol(self) -> str:
        return UNIT_SYMBOL[self.unit]

    @classmethod
    def parse(cls, token: str) -> Scalar:
        """Parse a string in to a Scalar

        Args:
            token (str): A string containing a scalar, e.g. "3.14fr"

        Raises:
            ScalarParseError: If the value is not a valid scalar

        Returns:
            Scalar: New scalar
        """
        match = _MATCH_SCALAR(token)
        if match is None:
            raise ScalarParseError(f"{token!r} is not a valid scalar")
        value, unit_name = match.groups()
        scalar = cls(float(value), SYMBOL_UNIT[unit_name or ""])
        return scalar


if __name__ == "__main__":

    print(Scalar.parse("3.14fr"))
    s = Scalar.parse("23")
    print(repr(s))
    print(repr(s.cells))
