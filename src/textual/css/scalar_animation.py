from __future__ import annotations

from typing import TYPE_CHECKING

from .scalar import ScalarOffset
from .._animator import Animation
from .._animator import EasingFunction
from .._types import CallbackType
from ..geometry import Offset

if TYPE_CHECKING:
    from ..widget import Widget
    from .styles import Styles


class ScalarAnimation(Animation):
    def __init__(
        self,
        widget: Widget,
        styles: Styles,
        start_time: float,
        attribute: str,
        value: ScalarOffset,
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
        self.easing = easing
        self.on_complete = on_complete

        size = widget.outer_size
        viewport = widget.app.size

        self.start: Offset = getattr(styles, attribute).resolve(size, viewport)
        self.destination: Offset = value.resolve(size, viewport)

        if speed is not None:
            distance = self.start.get_distance_to(self.destination)
            self.duration = distance / speed
        else:
            assert duration is not None, "Duration expected to be non-None"
            self.duration = duration

    def __call__(self, time: float) -> bool:
        factor = min(1.0, (time - self.start_time) / self.duration)
        eased_factor = self.easing(factor)

        if eased_factor >= 1:
            setattr(self.styles, self.attribute, self.final_value)
            return True

        if hasattr(self.start, "blend"):
            value = self.start.blend(self.destination, eased_factor)
        else:
            value = self.start + (self.destination - self.start) * eased_factor
        current = self.styles._rules.get(self.attribute)
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
