from __future__ import annotations

import logging
from .message_pump import MessagePump
from ._timer import Timer
from time import time
from typing import Callable

from dataclasses import dataclass


EasingFunction = Callable[[float], float]

LinearEasing = lambda value: value


def InOutCubitEasing(x: float) -> float:
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


log = logging.getLogger("rich")


@dataclass
class Animation:
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
    def __init__(self, obj: MessagePump) -> None:
        self.obj = obj
        self._animations: dict[str, Animation] = {}
        self._timer: Timer | None = None

    def animate(
        self,
        attribute: str,
        value: float,
        duration: float = 1,
        easing: EasingFunction = InOutCubitEasing,
    ) -> None:
        start_value = getattr(self.obj, attribute)
        start_time = time()

        animation = Animation(
            attribute=attribute,
            start_time=start_time,
            duration=duration,
            start_value=start_value,
            end_value=value,
            easing_function=easing,
        )
        self._animations[attribute] = animation
        if self._timer is None:
            self._timer = self.obj.set_interval(0.02, callback=self)

    async def __call__(self) -> None:
        log.debug("ANIMATION FRAME")
        animation_time = time()
        if all(
            animation(self.obj, animation_time)
            for animation in self._animations.values()
        ):
            if self._timer is not None:
                self._timer.stop()
                self._timer = None

        for _attribute, animation in self._animations.items():
            animation(self.obj, animation_time)
