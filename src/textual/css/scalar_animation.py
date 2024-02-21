from __future__ import annotations

from typing import TYPE_CHECKING

from .._animator import Animation, EasingFunction
from .._types import AnimationLevel, CallbackType
from .scalar import Scalar, ScalarOffset

if TYPE_CHECKING:
    from ..widget import Widget
    from .styles import StylesBase


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
        level: AnimationLevel = "full",
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
        self.level = level

        size = widget.outer_size
        viewport = widget.app.size

        self.start = getattr(styles, attribute).resolve(size, viewport)
        self.destination = value.resolve(size, viewport)

        if speed is not None:
            distance = self.start.get_distance_to(self.destination)
            self.duration = distance / speed
        else:
            assert duration is not None, "Duration expected to be non-None"
            self.duration = duration

    def __call__(
        self, time: float, app_animation_level: AnimationLevel = "full"
    ) -> bool:
        factor = min(1.0, (time - self.start_time) / self.duration)
        eased_factor = self.easing(factor)

        if (
            eased_factor >= 1
            or app_animation_level == "none"
            or app_animation_level == "basic"
            and self.level == "full"
        ):
            setattr(self.styles, self.attribute, self.final_value)
            return True

        if hasattr(self.start, "blend"):
            value = self.start.blend(self.destination, eased_factor)
        else:
            value = self.start + (self.destination - self.start) * eased_factor
        current = self.styles.get_rule(self.attribute)
        if current != value:
            setattr(self.styles, self.attribute, value)

        return False

    async def stop(self, complete: bool = True) -> None:
        """Stop the animation.

        Args:
            complete: Flag to say if the animation should be taken to completion.

        Note:
            [`on_complete`][Animation.on_complete] will be called regardless
            of the value provided for `complete`.
        """
        if complete:
            setattr(self.styles, self.attribute, self.final_value)
        await self.invoke_callback()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ScalarAnimation):
            return (
                self.final_value == other.final_value
                and self.duration == other.duration
            )
        return False
