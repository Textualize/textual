from __future__ import annotations

import asyncio
import sys
from math import pi, cos, sin, sqrt
from time import time
from tracemalloc import start
from typing import Callable, TypeVar

from dataclasses import dataclass

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


def _in_out_expo(x):
    """https://easings.net/#easeInOutExpo"""
    if 0 < x < 0.5:
        return pow(2, 20 * x - 10) / 2
    elif 0.5 <= x < 1:
        return (2 - pow(2, -20 * x + 10)) / 2
    else:
        return x    # x in (0, 1)


def _in_out_circ(x):
    """https://easings.net/#easeInOutCirc"""
    if x < 0.5:
        return (1 - sqrt(1 - pow(2 * x, 2))) / 2
    else:
        return (sqrt(1 - pow(-2 * x + 2, 2)) + 1) / 2


def _in_out_back(x):
    """https://easings.net/#easeInOutBack"""
    c = 1.70158 * 1.525
    if x < 0.5:
        return (pow(2 * x, 2) * ((c + 1) * 2 * x - c)) / 2
    else:
        return (pow(2 * x - 2, 2) * ((c + 1) * (x * 2 - 2) + c) + 2) / 2


def _in_elastic(x):
    """https://easings.net/#easeInElastic"""
    c = 2 * pi / 3;
    if 0 < x < 1:
        return -pow(2, 10 * x - 10) * sin((x * 10 - 10.75) * c)
    else:
        return x    # x in (0, 1)


def _in_out_elastic(x):
    """https://easings.net/#easeInOutElastic"""
    c = 2 * pi / 4.5
    if 0 < x < 0.5:
        return -(pow(2, 20 * x - 10) * sin((20 * x - 11.125) * c)) / 2
    elif 0.5 <= x < 1:
        return (pow(2, -20 * x + 10) * sin((20 * x - 11.125) * c)) / 2 + 1
    else:
        return x    # x in (0, 1)


def _out_elastic(x):
    """https://easings.net/#easeInOutElastic"""
    c = 2 * pi / 4.5
    if 0 < x < 0.5:
        return -(pow(2, 20 * x - 10) * sin((20 * x - 11.125) * c)) / 2
    elif 0.5 <= x < 1:
        return (pow(2, -20 * x + 10) * sin((20 * x - 11.125) * c)) / 2 + 1
    else:
        return x    # x in (0, 1)


def _out_bounce(x):
    """https://easings.net/#easeOutBounce"""
    n, d = 7.5625, 2.75
    if x < 1/d:
        return n * x * x
    elif x < 2/d:
        x_ = x - 1.5/d
        return n * x_ * x_ + 0.75
    elif x < 2.5/d:
        x_ = x - 2.25/d
        return n * x_ * x_ + 0.9375
    else:
        x_ = x - 2.625/d
        return n * x_ * x_ + 0.984375


def _in_bounce(x):
    """https://easings.net/#easeInBounce"""
    return 1 - _out_bounce(x)


def _in_out_bounce(x):
    """https://easings.net/#easeInOutBounce"""
    if x < 0.5:
        return (1 - _out_bounce(1 - 2 * x)) / 2
    else:
        return (1 + _out_bounce(2 * x - 1)) / 2


# https://easings.net/
EASING = {
    "none": lambda x: 1.0,
    "round": lambda x: 0.0 if x < 0.5 else 1.0,
    "linear": lambda x: x,
    "in_sine": lambda x: 1 - cos((x * pi) / 2),
    "in_out_sine": lambda x: -(cos(x * pi) - 1) / 2,
    "out_sine": lambda x: sin((x * pi) / 2),
    "in_quad": lambda x: x * x,
    "in_out_quad": lambda x: 2 * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 2) / 2,
    "out_quad": lambda x: 1 - pow(1 - x, 2),
    "in_cubic": lambda x: x * x * x,
    "in_out_cubic": lambda x: 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2,
    "out_cubic": lambda x: 1 - pow(1 - x, 3),
    "in_quart": lambda x: pow(x, 4),
    "in_out_quart": lambda x: 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2,
    "out_quart": lambda x: 1 - pow(1 - x, 4),
    "in_quint": lambda x: pow(x, 5),
    "in_out_quint": lambda x: 16 * pow(x, 5) if x < 0.5 else 1 - pow(-2 * x + 2, 5) / 2,
    "out_quint": lambda x: 1 - pow(1 - x, 5),
    "in_expo": lambda x: pow(2, 10 * x - 10) if x else 0,
    "in_out_expo": _in_out_expo,
    "out_expo": lambda x: 1 - pow(2, -10 * x) if x != 1 else 1,
    "in_circ": lambda x: 1 - sqrt(1 - pow(x, 2)),
    "in_out_circ": _in_out_circ,
    "out_circ": lambda x: sqrt(1 - pow(x - 1, 2)),
    "in_back": lambda x: 2.70158 * pow(x, 3) - 1.70158 * pow(x, 2),
    "in_out_back": _in_out_back,
    "out_back": lambda x: 1 + 2.70158 * pow(x - 1, 3) + 1.70158 * pow(x - 1, 2),
    "in_elastic": _in_elastic,
    "in_out_elastic": _in_out_elastic,
    "out_elastic": _out_elastic,
    "in_bounce": _in_bounce,
    "in_out_bounce": _in_out_bounce,
    "out_bounce": _out_bounce,
}

DEFAULT_EASING = "in_out_cubic"


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
