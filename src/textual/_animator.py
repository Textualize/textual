from __future__ import annotations

import asyncio
import sys
from time import time
from tracemalloc import start
from typing import Callable, TypeVar

from dataclasses import dataclass

from ._easing import DEFAULT_EASING, EASING
from ._timer import Timer
from ._types import MessageTarget

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


EasingFunction = Callable[[float], float]

T = TypeVar("T")


class Animatable(Protocol):
    def blend(self: T, destination: T, factor: float) -> T:
        ...


@dataclass
class Animation:
    obj: object
    attribute: str
    start_time: float
    duration: float
    start_value: float | Animatable
    end_value: float | Animatable
    easing_function: EasingFunction

    def __call__(self, time: float) -> bool:
        def blend_float(start: float, end: float, factor: float) -> float:
            return start + (end - start) * factor

        AnimatableT = TypeVar("AnimatableT", bound=Animatable)

        def blend(start: AnimatableT, end: AnimatableT, factor: float) -> AnimatableT:
            return start.blend(end, factor)

        blend_function = (
            blend_float if isinstance(self.start_value, (int, float)) else blend
        )

        if self.duration == 0:
            value = self.end_value
        else:
            factor = min(1.0, (time - self.start_time) / self.duration)
            eased_factor = self.easing_function(factor)
            # value = blend_function(self.start_value, self.end_value, eased_factor)

            if self.end_value > self.start_value:
                eased_factor = self.easing_function(factor)
                value = (
                    self.start_value
                    + (self.end_value - self.start_value) * eased_factor
                )
            else:
                eased_factor = 1 - self.easing_function(factor)
                value = (
                    self.end_value + (self.start_value - self.end_value) * eased_factor
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
        self._animations: dict[tuple[object, str], Animation] = {}
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
            self._timer_task = self._timer.start()

    async def stop(self) -> None:
        await self._timer.stop()
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

        start_time = time()

        animation_key = (obj, attribute)
        if animation_key in self._animations:
            self._animations[animation_key](start_time)

        start_value = getattr(obj, attribute)

        if start_value == value:
            self._animations.pop(animation_key, None)
            return

        if duration is not None:
            animation_duration = duration
        else:
            animation_duration = abs(value - start_value) / (speed or 50)
        easing_function = EASING[easing] if isinstance(easing, str) else easing
        animation = Animation(
            obj,
            attribute=attribute,
            start_time=start_time,
            duration=animation_duration,
            start_value=start_value,
            end_value=value,
            easing_function=easing_function,
        )
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
