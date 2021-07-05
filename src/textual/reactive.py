from __future__ import annotations

import sys
from typing import Callable, Generic, TypeVar

from .message_pump import MessagePump

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class Reactable(Protocol):
    def require_layout(self):
        ...

    def require_repaint(self):
        ...


ReactiveType = TypeVar("ReactiveType")


class Reactive(Generic[ReactiveType]):
    """Reactive descriptor."""

    def __init__(
        self,
        default: ReactiveType,
        *,
        layout: bool = False,
        repaint: bool = True,
    ) -> None:
        self._default = default
        self.layout = layout
        self.repaint = repaint

    def __set_name__(self, owner: Reactable, name: str) -> None:
        self.name = name
        self.internal_name = f"__{name}"
        setattr(owner, self.internal_name, self._default)

    def __get__(self, obj: Reactable, obj_type: type[object]) -> ReactiveType:
        return getattr(obj, self.internal_name)

    def __set__(self, obj: Reactable, value: ReactiveType) -> None:
        if getattr(obj, self.internal_name) != value:

            current_value = getattr(obj, self.internal_name, None)
            validate_function = getattr(obj, f"validate_{self.name}", None)
            if callable(validate_function):
                value = validate_function(value)

            if current_value != value:

                watch_function = getattr(obj, f"watch_{self.name}", None)
                if callable(watch_function):
                    watch_function(value)
                setattr(obj, self.internal_name, value)

                if self.layout:
                    obj.require_layout()
                elif self.repaint:
                    obj.require_repaint()
