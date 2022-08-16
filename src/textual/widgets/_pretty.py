from __future__ import annotations

from typing import Any
from rich.pretty import Pretty as PrettyRenderable
from ._static import Static


class Pretty(Static):
    def __init__(
        self,
        object: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._object = object
        super().__init__(
            PrettyRenderable(self._object),
            name=name,
            id=id,
            classes=classes,
        )
