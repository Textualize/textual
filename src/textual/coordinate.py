from __future__ import annotations

from typing import NamedTuple


class Coordinate(NamedTuple):
    """An object representing a row/column coordinate within a grid."""

    row: int
    column: int

    def left(self) -> Coordinate:
        """Get the coordinate to the left.

        Returns:
            Coordinate: The coordinate to the left.
        """
        row, column = self
        return Coordinate(row, column - 1)

    def right(self) -> Coordinate:
        """Get the coordinate to the right.

        Returns:
            Coordinate: The coordinate to the right.
        """
        row, column = self
        return Coordinate(row, column + 1)

    def up(self) -> Coordinate:
        """Get the coordinate above.

        Returns:
            Coordinate: The coordinate above.
        """
        row, column = self
        return Coordinate(row - 1, column)

    def down(self) -> Coordinate:
        """Get the coordinate below.

        Returns:
            Coordinate: The coordinate below.
        """
        row, column = self
        return Coordinate(row + 1, column)
