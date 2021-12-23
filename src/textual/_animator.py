from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
import sys
from time import time
from tracemalloc import start
from typing import Callable, TypeVar

from dataclasses import dataclass

from . import log
from ._easing import DEFAULT_EASING, EASING
from ._timer import Timer
from ._types import MessageTarget

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable


EasingFunction = Callable[[float], float]

T = TypeVar("T")


@runtime_checkable
class Animatable(Protocol):
    def blend(self: T, destination: T, factor: float) -> T:
        ...


class Animation(ABC):
    @abstractmethod
    def __call__(self, time: float) -> bool:
        raise NotImplementedError("")


@dataclass
class SimpleAnimation(Animation):
    obj: object
    attribute: str
    start_time: float
    duration: float
    start_value: float | Animatable
    end_value: float | Animatable
    easing: EasingFunction

    def __call__(self, time: float) -> bool:
        def blend_float(start: float, end: float, factor: float) -> float:
            return start + (end - start) * factor

        AnimatableT = TypeVar("AnimatableT", bound=Animatable)

        def blend(start: AnimatableT, end: AnimatableT, factor: float) -> AnimatableT:
            return start.blend(end, factor)

        if self.duration == 0:
            value = self.end_value
        else:
            factor = min(1.0, (time - self.start_time) / self.duration)
            eased_factor = self.easing(factor)

            log("ANIMATE", self.start_value, self.end_value)
            if isinstance(self.start_value, Animatable):
                assert isinstance(
                    self.end_value, Animatable, "end_value must be animatable"
                )
                value = self.start_value.blend(self.end_value, eased_factor)
            else:
                assert isinstance(
                    self.start_value, float
                ), "`start_value` must be float"
                assert isinstance(self.end_value, float), "`end_value` must be float"
                if self.end_value > self.start_value:
                    eased_factor = self.easing(factor)
                    value = (
                        self.start_value
                        + (self.end_value - self.start_value) * eased_factor
                    )
                else:
                    eased_factor = 1 - self.easing(factor)
                    value = (
                        self.end_value
                        + (self.start_value - self.end_value) * eased_factor
                    )
        setattr(self.obj, self.attribute, value)
        return value == self.end_value


class BoundAnimator:
    def __init__(self, animator: Animator, obj: object) -> None:
        self._animator = animator
        self._obj = obj

    def __call__(
        self,
        attribute: str,
        value: float,
        *,
        duration: float | None = None,
        speed: float | None = None,
        easing: EasingFunction | str = DEFAULT_EASING,
    ) -> None:
        easing_function = EASING[easing] if isinstance(easing, str) else easing
        self._animator.animate(
            self._obj,
            attribute=attribute,
            value=value,
            duration=duration,
            speed=speed,
            easing=easing_function,
        )


class Animator:
    def __init__(self, target: MessageTarget, frames_per_second: int = 60) -> None:
        self._animations: dict[tuple[object, str], SimpleAnimation] = {}
        self._timer = Timer(
            target,
            1 / frames_per_second,
            target,
            name="Animator",
            callback=self,
            pause=True,
        )
        self._timer_task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._timer_task is None:
            self._timer_task = asyncio.get_event_loop().create_task(self._timer.run())

    async def stop(self) -> None:
        self._timer.stop()
        if self._timer_task:
            await self._timer_task
        self._timer_task = None

    def bind(self, obj: object) -> BoundAnimator:
        return BoundAnimator(self, obj)

    def animate(
        self,
        obj: object,
        attribute: str,
        value: float,
        *,
        duration: float | None = None,
        speed: float | None = None,
        easing: EasingFunction | str = DEFAULT_EASING,
    ) -> None:
        log("animate", obj, attribute, value)
        start_time = time()

        animation_key = (id(obj), attribute)
        if animation_key in self._animations:
            self._animations[animation_key](start_time)

        easing_function = EASING[easing] if isinstance(easing, str) else easing

        animation: Animation | None = None
        if hasattr(obj, "__textual_animation__"):
            animation = getattr(obj, "__textual_animation__")(
                attribute,
                value,
                start_time,
                duration=duration,
                speed=speed,
                easing=easing,
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
                easing=easing_function,
            )
        assert animation is not None, "animation expected to be non-None"
        self._animations[animation_key] = animation
        self._timer.resume()

    async def __call__(self) -> None:
        if not self._animations:
            self._timer.pause()
        else:
            animation_time = time()
            animation_keys = list(self._animations.keys())
            for animation_key in animation_keys:
                animation = self._animations[animation_key]
                if animation(animation_time):
                    del self._animations[animation_key]
