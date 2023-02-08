from __future__ import annotations

from typing_extensions import TYPE_CHECKING

import rich.repr

from .scalar import ScalarOffset, Scalar
from .._animator import Animation
from .._animator import EasingFunction
from .._types import CallbackType


if TYPE_CHECKING:
    from ..dom import DOMNode
    from ..widget import Widget
    from .styles import StylesBase


@rich.repr.auto
class ScalarAnimation(Animation):
    def __init__(
        self,
        widget: Widget,
        styles: StylesBase,
        start_time: float,
        attribute: str,
        value: ScalarOffset | Scalar,
        duration: float | None,
        speed: float | None,
        easing: EasingFunction,
        on_complete: CallbackType | None = None,
    ):
        assert (
            speed is not None or duration is not None
        ), "One of speed or duration required"
        self.widget = widget
        self.styles = styles
        self.start_time = start_time
        self.attribute = attribute
        self.final_value = value
        self._duration = duration
        self.speed = speed
        self.easing = easing
        self.on_complete = on_complete
        self._started = False

    def _start_animation(self) -> None:
        size = self.widget.outer_size
        viewport = self.widget.app.size

        self.start = getattr(self.styles, self.attribute).resolve(size, viewport)
        self.destination = self.final_value.resolve(size, viewport)

        if self.speed is not None:
            distance = self.start.get_distance_to(self.destination)
            self.duration = distance / self.speed
        else:
            assert self._duration is not None
            self.duration = self._duration
        self._started = True

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.widget
        yield "styles", self.styles
        yield "start_time", self.start_time
        yield "attribute", self.attribute
        yield "final_value", self.final_value
        yield "easing", self.easing
        yield "on_complete", self.on_complete

    def __call__(self, time: float) -> bool:
        if not self._started:
            if self.widget.display and self.widget.region:
                self._start_animation()
            else:
                return False
        factor = min(1.0, (time - self.start_time) / self.duration)
        eased_factor = self.easing(factor)

        if eased_factor >= 1:
            setattr(self.styles, self.attribute, self.final_value)
            return True

        if hasattr(self.start, "blend"):
            value = self.start.blend(self.destination, eased_factor)
        else:
            value = self.start + (self.destination - self.start) * eased_factor
        current = self.styles.get_rule(self.attribute)
        if current != value:
            setattr(self.styles, f"{self.attribute}", value)

        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ScalarAnimation):
            return (
                self.final_value == other.final_value
                and self.duration == other.duration
            )
        return False
