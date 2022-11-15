from __future__ import annotations

import asyncio
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from . import _clock
from ._callback import invoke
from ._easing import DEFAULT_EASING, EASING
from ._types import CallbackType
from .timer import Timer

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:  # pragma: no cover
    from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from textual.app import App

EasingFunction = Callable[[float], float]


class AnimationError(Exception):
    """An issue prevented animation from starting."""


T = TypeVar("T")


@runtime_checkable
class Animatable(Protocol):
    def blend(self: T, destination: T, factor: float) -> T:  # pragma: no cover
        ...


class Animation(ABC):
    on_complete: CallbackType | None = None
    """Callback to run after animation completes"""

    @abstractmethod
    def __call__(self, time: float) -> bool:  # pragma: no cover
        """Call the animation, return a boolean indicating whether animation is in-progress or complete.

        Args:
            time (float): The current timestamp

        Returns:
            bool: True if the animation has finished, otherwise False.
        """
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
    on_complete: CallbackType | None = None

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
        value: str | float | Animatable,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        delay: float = 0.0,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Animate an attribute.

        Args:
            attribute (str): Name of the attribute to animate.
            value (float | Animatable): The value to animate to.
            final_value (object, optional): The final value of the animation. Defaults to `value` if not set.
            duration (float | None, optional): The duration of the animate. Defaults to None.
            speed (float | None, optional): The speed of the animation. Defaults to None.
            delay (float, optional): A delay (in seconds) before the animation starts. Defaults to 0.0.
            easing (EasingFunction | str, optional): An easing method. Defaults to "in_out_cubic".
            on_complete (CallbackType | None, optional): A callable to invoke when the animation is finished. Defaults to None.

        """
        start_value = getattr(self._obj, attribute)
        if isinstance(value, str) and hasattr(start_value, "parse"):
            # Color and Scalar have a parse method
            # I'm exploiting a coincidence here, but I think this should be a first-class concept
            # TODO: add a `Parsable` protocol
            value = start_value.parse(value)
        easing_function = EASING[easing] if isinstance(easing, str) else easing
        return self._animator.animate(
            self._obj,
            attribute=attribute,
            value=value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            delay=delay,
            easing=easing_function,
            on_complete=on_complete,
        )


class Animator:
    """An object to manage updates to a given attribute over a period of time."""

    def __init__(self, app: App, frames_per_second: int = 60) -> None:
        self._animations: dict[tuple[object, str], Animation] = {}
        self.app = app
        self._timer = Timer(
            app,
            1 / frames_per_second,
            app,
            name="Animator",
            callback=self,
            pause=True,
        )
        self._idle_event = asyncio.Event()

    async def start(self) -> None:
        """Start the animator task."""
        self._idle_event.set()
        self._timer.start()

    async def stop(self) -> None:
        """Stop the animator task."""
        try:
            await self._timer.stop()
        except asyncio.CancelledError:
            pass
        finally:
            self._idle_event.set()

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
        delay: float = 0.0,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Animate an attribute to a new value.

        Args:
            obj (object): The object containing the attribute.
            attribute (str): The name of the attribute.
            value (Any): The destination value of the attribute.
            final_value (Any, optional): The final value, or ellipsis if it is the same as ``value``. Defaults to Ellipsis/
            duration (float | None, optional): The duration of the animation, or ``None`` to use speed. Defaults to ``None``.
            speed (float | None, optional): The speed of the animation. Defaults to None.
            easing (EasingFunction | str, optional): An easing function. Defaults to DEFAULT_EASING.
            delay (float, optional): Number of seconds to delay the start of the animation by. Defaults to 0.
            on_complete (CallbackType | None, optional): Callback to run after the animation completes.
        """
        animate_callback = partial(
            self._animate,
            obj,
            attribute,
            value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            easing=easing,
            on_complete=on_complete,
        )
        if delay:
            self.app.set_timer(delay, animate_callback)
        else:
            animate_callback()

    def _animate(
        self,
        obj: object,
        attribute: str,
        value: Any,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
    ):
        """Animate an attribute to a new value.

        Args:
            obj (object): The object containing the attribute.
            attribute (str): The name of the attribute.
            value (Any): The destination value of the attribute.
            final_value (Any, optional): The final value, or ellipsis if it is the same as ``value``. Defaults to ....
            duration (float | None, optional): The duration of the animation, or ``None`` to use speed. Defaults to ``None``.
            speed (float | None, optional): The speed of the animation. Defaults to None.
            easing (EasingFunction | str, optional): An easing function. Defaults to DEFAULT_EASING.
            on_complete (CallbackType | None, optional): Callback to run after the animation completes.
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
                getattr(obj, attribute),
                value,
                start_time,
                duration=duration,
                speed=speed,
                easing=easing_function,
                on_complete=on_complete,
            )

        if animation is None:

            if not isinstance(value, (int, float)) and not isinstance(
                value, Animatable
            ):
                raise AnimationError(
                    f"Don't know how to animate {value!r}; "
                    "Can only animate <int>, <float>, or objects with a blend method"
                )

            start_value = getattr(obj, attribute)

            if start_value == value:
                self._animations.pop(animation_key, None)
                return

            if duration is not None:
                animation_duration = duration
            else:
                if hasattr(value, "get_distance_to"):
                    animation_duration = value.get_distance_to(start_value) / (
                        speed or 50
                    )
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
                on_complete=on_complete,
            )
        assert animation is not None, "animation expected to be non-None"

        current_animation = self._animations.get(animation_key)
        if current_animation is not None and current_animation == animation:
            return

        self._animations[animation_key] = animation
        self._timer.resume()
        self._idle_event.clear()

    async def __call__(self) -> None:
        if not self._animations:
            self._timer.pause()
            self._idle_event.set()
        else:
            animation_time = self._get_time()
            animation_keys = list(self._animations.keys())
            for animation_key in animation_keys:
                animation = self._animations[animation_key]
                animation_complete = animation(animation_time)
                if animation_complete:
                    completion_callback = animation.on_complete
                    if completion_callback is not None:
                        await invoke(completion_callback)
                    del self._animations[animation_key]

    def _get_time(self) -> float:
        """Get the current wall clock time, via the internal Timer."""
        # N.B. We could remove this method and always call `self._timer.get_time()` internally,
        # but it's handy to have in mocking situations
        return _clock.get_time_no_wait()

    async def wait_for_idle(self) -> None:
        """Wait for any animations to complete."""
        await self._idle_event.wait()
