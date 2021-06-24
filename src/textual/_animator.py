from __future__ import annotations

import logging

import asyncio
from time import time
from typing import Callable

from dataclasses import dataclass

from ._timer import Timer
from ._types import MessageTarget
from .message_pump import MessagePump

EasingFunction = Callable[[float], float]


LinearEasing = lambda value: value


def InOutCubitEasing(x: float) -> float:
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


log = logging.getLogger("rich")


@dataclass
class Animation:
    obj: object
    attribute: str
    start_time: float
    duration: float
    start_value: float
    end_value: float
    easing_function: EasingFunction

    def __call__(self, obj: object, time: float) -> bool:
        progress = min(1.0, (time - self.start_time) / self.duration)
        eased_progress = self.easing_function(progress)
        value = self.start_value + (self.end_value - self.start_value) * eased_progress
        setattr(obj, self.attribute, value)
        return value == self.end_value


class Animator:
    def __init__(self, target: MessageTarget) -> None:
        self._animations: dict[tuple[object, str], Animation] = {}
        self._timer: Timer = Timer(target, 1 / 30, target, callback=self)

    async def start(self) -> None:
        asyncio.get_event_loop().create_task(self._timer.run())

    async def stop(self) -> None:
        self._timer.stop()

    def animate(
        self,
        obj: object,
        attribute: str,
        value: float,
        duration: float = 1,
        easing: EasingFunction = InOutCubitEasing,
    ) -> None:
        start_value = getattr(obj, attribute)
        start_time = time()

        animation = Animation(
            obj,
            attribute=attribute,
            start_time=start_time,
            duration=duration,
            start_value=start_value,
            end_value=value,
            easing_function=easing,
        )
        self._animations[(obj, attribute)] = animation

    async def __call__(self) -> None:
        log.debug("ANIMATION FRAME")
        animation_time = time()
        animation_keys = list(self._animations.keys())
        for animation_key in animation_keys:
            animation = self._animations[animation_key]
            obj, _attribute = animation_key
            if animation(obj, animation_time):
                del self._animations[animation_key]
