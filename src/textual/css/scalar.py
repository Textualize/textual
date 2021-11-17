from __future__ import annotations

import re
from typing import NamedTuple


_MATCH_SCALAR = re.compile(r"^(\d+\.?\d*)(fr|%)?$").match


class ScalarParseError(Exception):
    pass


class Scalar(NamedTuple):
    """A numeric value and a unit."""

    value: float
    unit: str

    def __str__(self) -> str:
        value, unit = self
        return f"{int(value) if value.is_integer() else value}{unit}"

    @property
    def cells(self) -> int | None:
        value, unit = self
        if unit:
            return None
        else:
            return int(value)

    @property
    def fraction(self) -> int | None:
        value, unit = self
        if unit == "fr":
            return int(value)
        else:
            return None

    def resolve_size(self, total: int, total_fraction: int) -> int:
        value, unit = self
        if unit == "":
            return int(value)
        elif unit == "%":
            return int(total * value / 100.0)
        else:  #  if unit == "fr":
            return int((value / total_fraction) * total)

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
        value, unit = match.groups()
        scalar = cls(float(value), unit or "")
        return scalar


if __name__ == "__main__":

    print(Scalar.parse("3.14"))
