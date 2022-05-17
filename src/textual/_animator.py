from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
import sys
from typing import Any, Callable, TypeVar

from dataclasses import dataclass

from . import _clock
from ._easing import DEFAULT_EASING, EASING
from ._timer import Timer
from ._types import MessageTarget

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:  # pragma: no cover
    from typing_extensions import Protocol, runtime_checkable


EasingFunction = Callable[[float], float]

T = TypeVar("T")


@runtime_checkable
class Animatable(Protocol):
    def blend(self: T, destination: T, factor: float) -> T:  # pragma: no cover
        ...


class Animation(ABC):
    @abstractmethod
    def __call__(self, time: float) -> bool:  # pragma: no cover
        raise NotImplementedError("")

    def __eq__(self, other: object) -> bool:
        return False


@dataclass
class SimpleAnimation(Animation):
    obj: object
    attribute: str
    start_time: float
    duration: float
    start_value: float | Animatable
    end_value: float | Animatable
    final_value: object
    easing: EasingFunction

    def __call__(self, time: float) -> bool:

        if self.duration == 0:
            setattr(self.obj, self.attribute, self.final_value)
            return True

        factor = min(1.0, (time - self.start_time) / self.duration)
        eased_factor = self.easing(factor)

        if factor == 1.0:
            value = self.final_value
        elif isinstance(self.start_value, Animatable):
            assert isinstance(
                self.end_value, Animatable
            ), "end_value must be animatable"
            value = self.start_value.blend(self.end_value, eased_factor)
        else:
            assert isinstance(
                self.start_value, (int, float)
            ), f"`start_value` must be float, not {self.start_value!r}"
            assert isinstance(
                self.end_value, (int, float)
            ), f"`end_value` must be float, not {self.end_value!r}"
            if self.end_value > self.start_value:
                eased_factor = self.easing(factor)
                value = (
                    self.start_value
                    + (self.end_value - self.start_value) * eased_factor
                )
            else:
                eased_factor = 1 - self.easing(factor)
                value = (
                    self.end_value + (self.start_value - self.end_value) * eased_factor
                )
        setattr(self.obj, self.attribute, value)
        return factor >= 1

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SimpleAnimation):
            return (
                self.final_value == other.final_value
                and self.duration == other.duration
            )
        return False


class BoundAnimator:
    def __init__(self, animator: Animator, obj: object) -> None:
        self._animator = animator
        self._obj = obj

    def __call__(
        self,
        attribute: str,
        value: float,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        easing: EasingFunction | str = DEFAULT_EASING,
    ) -> None:
        easing_function = EASING[easing] if isinstance(easing, str) else easing
        return self._animator.animate(
            self._obj,
            attribute=attribute,
            value=value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            easing=easing_function,
        )


class Animator:
    """An object to manage updates to a given attribute over a period of time."""

    def __init__(self, target: MessageTarget, frames_per_second: int = 60) -> None:
        self._animations: dict[tuple[object, str], Animation] = {}
        self.target = target
        self._timer = Timer(
            target,
            1 / frames_per_second,
            target,
            name="Animator",
            callback=self,
            pause=True,
        )

    async def start(self) -> None:
        """Start the animator task."""

        self._timer.start()

    async def stop(self) -> None:
        """Stop the animator task."""
        try:
            await self._timer.stop()
        except asyncio.CancelledError:
            pass

    def bind(self, obj: object) -> BoundAnimator:
        """Bind the animator to a given objects."""
        return BoundAnimator(self, obj)

    def animate(
        self,
        obj: object,
        attribute: str,
        value: Any,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        easing: EasingFunction | str = DEFAULT_EASING,
    ) -> None:
        """Animate an attribute to a new value.

        Args:
            obj (object): The object containing the attribute.
            attribute (str): The name of the attribute.
            value (Any): The destination value of the attribute.
            final_value (Any, optional): The final value, or ellipsis if it is the same as ``value``. Defaults to ....
            duration (float | None, optional): The duration of the animation, or ``None`` to use speed. Defaults to ``None``.
            speed (float | None, optional): The speed of the animation. Defaults to None.
            easing (EasingFunction | str, optional): An easing function. Defaults to DEFAULT_EASING.
        """

        if not hasattr(obj, attribute):
            raise AttributeError(
                f"Can't animate attribute {attribute!r} on {obj!r}; attribute does not exist"
            )
        assert (duration is not None and speed is None) or (
            duration is None and speed is not None
        ), "An Animation should have a duration OR a speed"

        if final_value is ...:
            final_value = value
        start_time = self._get_time()

        animation_key = (id(obj), attribute)

        easing_function = EASING[easing] if isinstance(easing, str) else easing

        animation: Animation | None = None
        if hasattr(obj, "__textual_animation__"):
            animation = getattr(obj, "__textual_animation__")(
                attribute,
                value,
                start_time,
                duration=duration,
                speed=speed,
                easing=easing_function,
            )
        if animation is None:
            start_value = getattr(obj, attribute)

            if start_value == value:
                self._animations.pop(animation_key, None)
                return

            if duration is not None:
                animation_duration = duration
            else:
                animation_duration = abs(value - start_value) / (speed or 50)

            animation = SimpleAnimation(
                obj,
                attribute=attribute,
                start_time=start_time,
                duration=animation_duration,
                start_value=start_value,
                end_value=value,
                final_value=final_value,
                easing=easing_function,
            )
        assert animation is not None, "animation expected to be non-None"

        current_animation = self._animations.get(animation_key)
        if current_animation is not None and current_animation == animation:
            return

        self._animations[animation_key] = animation
        self._timer.resume()

    def __call__(self) -> None:
        if not self._animations:
            self._timer.pause()
        else:
            animation_time = self._get_time()
            animation_keys = list(self._animations.keys())
            for animation_key in animation_keys:
                animation = self._animations[animation_key]
                if animation(animation_time):
                    del self._animations[animation_key]

    def _get_time(self) -> float:
        """Get the current wall clock time, via the internal Timer."""
        # N.B. We could remove this method and always call `self._timer.get_time()` internally,
        # but it's handy to have in mocking situations
        return _clock.get_time()
