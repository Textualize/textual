from abc import ABC, abstractmethod
from typing import Iterable

from textual.content import Style
from textual.strip import Strip


class Visual(ABC):
    """A Textual 'visual' object.

    Analogous to a Rich renderable, but with support for transparency.

    """

    @abstractmethod
    def textualize(
        self, base_style: Style, width: int, height: int | None
    ) -> Iterable[Strip]:
        """Render the visual in to an iterable of strips.

        Args:
            base_style: The base style.
            width: Width of desired render.
            height: Height of desired render.

        Returns:
            An iterable of Strips.
        """

    @abstractmethod
    def get_optimal_width(self) -> int:
        """Get ideal width of the renderable to display its content.

        Returns:
            A width in cells.

        """

    @abstractmethod
    def get_minimal_width(self) -> int:
        """Get the minimal width (the small width that doesn't lose information).

        Returns:
            A width in cells.
        """

    @abstractmethod
    def get_height(self, width: int) -> int:
        """Get the height of the visual if rendered with the given width.

        Returns:
            A height in lines.
        """
