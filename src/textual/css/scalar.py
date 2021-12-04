from __future__ import annotations

from enum import Enum, unique
import re
from typing import Iterable, NamedTuple

import rich.repr

from ..geometry import Offset


class ScalarError(Exception):
    pass


class ScalarResolveError(ScalarError):
    pass


class ScalarParseError(ScalarError):
    pass


@unique
class Unit(Enum):
    CELLS = 1
    FRACTION = 2
    PERCENT = 3
    WIDTH = 4
    HEIGHT = 5
    VIEW_WIDTH = 6
    VIEW_HEIGHT = 7
    MILLISECONDS = 8
    SECONDS = 9


UNIT_SYMBOL = {
    Unit.CELLS: "",
    Unit.FRACTION: "fr",
    Unit.PERCENT: "%",
    Unit.WIDTH: "w",
    Unit.HEIGHT: "h",
    Unit.VIEW_WIDTH: "vw",
    Unit.VIEW_HEIGHT: "vh",
    Unit.MILLISECONDS: "ms",
    Unit.SECONDS: "s",
}

SYMBOL_UNIT = {v: k for k, v in UNIT_SYMBOL.items()}

_MATCH_SCALAR = re.compile(r"^(\-?\d+\.?\d*)(fr|%|w|h|vw|vh|s|ms)?$").match


RESOLVE_MAP = {
    Unit.CELLS: lambda value, size, viewport: value,
    Unit.WIDTH: lambda value, size, viewport: size[0] * value / 100,
    Unit.HEIGHT: lambda value, size, viewport: size[1] * value / 100,
    Unit.VIEW_WIDTH: lambda value, size, viewport: viewport[0] * value / 100,
    Unit.VIEW_HEIGHT: lambda value, size, viewport: viewport[1] * value / 100,
}


def get_symbols(units: Iterable[Unit]) -> list[str]:
    """Get symbols for an iterable of units.

    Args:
        units (Iterable[Unit]): A number of units.

    Returns:
        list[str]: List of symbols.
    """
    return [UNIT_SYMBOL[unit] for unit in units]


class Scalar(NamedTuple):
    """A numeric value and a unit."""

    value: float
    unit: Unit
    percent_unit: Unit

    def __str__(self) -> str:
        value, _unit, _ = self
        return f"{int(value) if value.is_integer() else value}{self.symbol}"

    @property
    def is_percent(self) -> bool:
        return self.unit == Unit.PERCENT

    @property
    def cells(self) -> int | None:
        value, unit, _ = self
        return int(value) if unit == Unit.CELLS else None

    @property
    def fraction(self) -> int | None:
        value, unit, _ = self
        return int(value) if unit == Unit.FRACTION else None

    @property
    def symbol(self) -> str:
        return UNIT_SYMBOL[self.unit]

    @classmethod
    def from_number(cls, value: float) -> Scalar:
        return cls(float(value), Unit.CELLS, Unit.WIDTH)

    @classmethod
    def parse(cls, token: str, percent_unit: Unit = Unit.WIDTH) -> Scalar:
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
        scalar = cls(float(value), SYMBOL_UNIT[unit_name or ""], percent_unit)
        return scalar

    def resolve_dimension(
        self, size: tuple[int, int], viewport: tuple[int, int]
    ) -> float:
        value, unit, percent_unit = self
        if unit == Unit.PERCENT:
            unit = percent_unit
        try:
            return RESOLVE_MAP[unit](value, size, viewport)
        except KeyError:
            raise ScalarResolveError(f"expected dimensions; found {str(self)!r}")

    def resolve_time(self) -> float:
        value, unit, _ = self
        if unit == Unit.MILLISECONDS:
            return value / 1000.0
        elif unit == Unit.SECONDS:
            return value
        raise ScalarResolveError(f"expected time; found {str(self)!r}")


@rich.repr.auto(angular=True)
class ScalarOffset(NamedTuple):
    x: Scalar
    y: Scalar

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, str(self.x)
        yield None, str(self.y)

    def resolve(self, size: tuple[int, int], viewport: tuple[int, int]) -> Offset:
        x, y = self
        return Offset(
            round(x.resolve_dimension(size, viewport)),
            round(y.resolve_dimension(size, viewport)),
        )


if __name__ == "__main__":

    print(Scalar.parse("3.14fr"))
    s = Scalar.parse("23")
    print(repr(s))
    print(repr(s.cells))
