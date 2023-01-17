from __future__ import annotations

from typing import NamedTuple


class Coordinate(NamedTuple):
    """An object representing a row/column coordinate."""

    row: int
    column: int

    def left(self) -> Coordinate:
        """Get coordinate to the left.

        Returns:
            Coordinate: The coordinate.
        """
        row, column = self
        return Coordinate(row, column - 1)

    def right(self) -> Coordinate:
        """Get coordinate to the right.

        Returns:
            Coordinate: The coordinate.
        """
        row, column = self
        return Coordinate(row, column + 1)

    def up(self) -> Coordinate:
        """Get coordinate above.

        Returns:
            Coordinate: The coordinate.
        """
        row, column = self
        return Coordinate(row - 1, column)

    def down(self) -> Coordinate:
        """Get coordinate below.

        Returns:
            Coordinate: The coordinate.
        """
        row, column = self
        return Coordinate(row + 1, column)
