"""Provides a pretty-printing widget."""

from __future__ import annotations

from typing import Any

from rich.pretty import Pretty as PrettyRenderable

from textual.widget import Widget


class Pretty(Widget):
    """A pretty-printing widget.

    Used to pretty-print any object.
    """

    DEFAULT_CSS = """
    Pretty {
        height: auto;
    }
    """

    def __init__(
        self,
        object: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialise the `Pretty` widget.

        Args:
            object: The object to pretty-print.
            name: The name of the pretty widget.
            id: The ID of the pretty in the DOM.
            classes: The CSS classes of the pretty.
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
        )
        self._renderable = PrettyRenderable(object)

    def render(self) -> PrettyRenderable:
        """Render the pretty-printed object.

        Returns:
            The rendered pretty-print.
        """
        return self._renderable

    def update(self, object: Any) -> None:
        """Update the content of the pretty widget.

        Args:
            object: The object to pretty-print.
        """
        self._renderable = PrettyRenderable(object)
        self.clear_cached_dimensions()
        self.refresh(layout=True)
