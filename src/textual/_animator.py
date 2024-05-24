from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from typing_extensions import Protocol, runtime_checkable

from . import _time
from ._callback import invoke
from ._easing import DEFAULT_EASING, EASING
from ._types import AnimationLevel, CallbackType
from .timer import Timer

if TYPE_CHECKING:
    from textual.app import App

    AnimationKey = tuple[int, str]
    """Animation keys are the id of the object and the attribute being animated."""

EasingFunction = Callable[[float], float]
"""Signature for a function that parametrises animation speed.

An easing function must map the interval [0, 1] into the interval [0, 1].
"""


class AnimationError(Exception):
    """An issue prevented animation from starting."""


ReturnType = TypeVar("ReturnType")


@runtime_checkable
class Animatable(Protocol):
    """Protocol for objects that can have their intrinsic values animated.

    For example, the transition between two colors can be animated
    because the class [`Color`][textual.color.Color.blend] satisfies this protocol.
    """

    def blend(
        self: ReturnType, destination: ReturnType, factor: float
    ) -> ReturnType:  # pragma: no cover
        ...


class Animation(ABC):
    on_complete: CallbackType | None = None
    """Callback to run after animation completes"""

    @abstractmethod
    def __call__(
        self,
        time: float,
        app_animation_level: AnimationLevel = "full",
    ) -> bool:  # pragma: no cover
        """Call the animation, return a boolean indicating whether animation is in-progress or complete.

        Args:
            time: The current timestamp

        Returns:
            True if the animation has finished, otherwise False.
        """
        raise NotImplementedError("")

    async def invoke_callback(self) -> None:
        """Calls the [`on_complete`][Animation.on_complete] callback if one is provided."""
        if self.on_complete is not None:
            await invoke(self.on_complete)

    @abstractmethod
    async def stop(self, complete: bool = True) -> None:
        """Stop the animation.

        Args:
            complete: Flag to say if the animation should be taken to completion.
        """
        raise NotImplementedError

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
    level: AnimationLevel = "full"
    """Minimum level required for the animation to take place (inclusive)."""

    def __call__(
        self, time: float, app_animation_level: AnimationLevel = "full"
    ) -> bool:
        if (
            self.duration == 0
            or app_animation_level == "none"
            or app_animation_level == "basic"
            and self.level == "full"
        ):
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

    async def stop(self, complete: bool = True) -> None:
        """Stop the animation.

        Args:
            complete: Flag to say if the animation should be taken to completion.

        Note:
            [`on_complete`][Animation.on_complete] will be called regardless
            of the value provided for `complete`.
        """
        if complete:
            setattr(self.obj, self.attribute, self.end_value)
        await self.invoke_callback()

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
        level: AnimationLevel = "full",
    ) -> None:
        """Animate an attribute.

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation. Defaults to `value` if not set.
            duration: The duration (in seconds) of the animation.
            speed: The speed of the animation.
            delay: A delay (in seconds) before the animation starts.
            easing: An easing method.
            on_complete: A callable to invoke when the animation is finished.
            level: Minimum level required for the animation to take place (inclusive).
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
            level=level,
        )


class Animator:
    """An object to manage updates to a given attribute over a period of time."""

    def __init__(self, app: App, frames_per_second: int = 60) -> None:
        """Initialise the animator object.

        Args:
            app: The application that owns the animator.
            frames_per_second: The number of frames/second to run the animation at.
        """
        self._animations: dict[AnimationKey, Animation] = {}
        """Dictionary that maps animation keys to the corresponding animation instances."""
        self._scheduled: dict[AnimationKey, Timer] = {}
        """Dictionary of scheduled animations, comprising of their keys and the timer objects."""
        self.app = app
        """The app that owns the animator object."""
        self._timer = Timer(
            app,
            1 / frames_per_second,
            name="Animator",
            callback=self,
            pause=True,
        )
        """The timer that runs the animator."""
        self._idle_event = asyncio.Event()
        """Flag if no animations are currently taking place."""
        self._complete_event = asyncio.Event()
        """Flag if no animations are currently taking place and none are scheduled."""

    async def start(self) -> None:
        """Start the animator task."""
        self._idle_event.set()
        self._complete_event.set()
        self._timer._start()

    async def stop(self) -> None:
        """Stop the animator task."""
        try:
            self._timer.stop()
        except asyncio.CancelledError:
            pass
        finally:
            self._idle_event.set()
            self._complete_event.set()

    def bind(self, obj: object) -> BoundAnimator:
        """Bind the animator to a given object.

        Args:
            obj: The object to bind to.

        Returns:
            The bound animator.
        """
        return BoundAnimator(self, obj)

    def is_being_animated(self, obj: object, attribute: str) -> bool:
        """Does the object/attribute pair have an ongoing or scheduled animation?

        Args:
            obj: An object to check for.
            attribute: The attribute on the object to test for.

        Returns:
            `True` if that attribute is being animated for that object, `False` if not.
        """
        key = (id(obj), attribute)
        return key in self._animations or key in self._scheduled

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
        level: AnimationLevel = "full",
    ) -> None:
        """Animate an attribute to a new value.

        Args:
            obj: The object containing the attribute.
            attribute: The name of the attribute.
            value: The destination value of the attribute.
            final_value: The final value, or ellipsis if it is the same as ``value``.
            duration: The duration of the animation, or ``None`` to use speed.
            speed: The speed of the animation.
            easing: An easing function.
            delay: Number of seconds to delay the start of the animation by.
            on_complete: Callback to run after the animation completes.
            level: Minimum level required for the animation to take place (inclusive).
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
            level=level,
        )
        if delay:
            self._complete_event.clear()
            self._scheduled[(id(obj), attribute)] = self.app.set_timer(
                delay, animate_callback
            )
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
        level: AnimationLevel = "full",
    ) -> None:
        """Animate an attribute to a new value.

        Args:
            obj: The object containing the attribute.
            attribute: The name of the attribute.
            value: The destination value of the attribute.
            final_value: The final value, or ellipsis if it is the same as ``value``.
            duration: The duration of the animation, or ``None`` to use speed.
            speed: The speed of the animation.
            easing: An easing function.
            on_complete: Callback to run after the animation completes.
            level: Minimum level required for the animation to take place (inclusive).
        """
        if not hasattr(obj, attribute):
            raise AttributeError(
                f"Can't animate attribute {attribute!r} on {obj!r}; attribute does not exist"
            )
        assert (duration is not None and speed is None) or (
            duration is None and speed is not None
        ), "An Animation should have a duration OR a speed"

        # If an animation is already scheduled for this attribute, unschedule it.
        animation_key = (id(obj), attribute)
        try:
            del self._scheduled[animation_key]
        except KeyError:
            pass

        if final_value is ...:
            final_value = value

        start_time = self._get_time()
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
                level=level,
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
                on_complete=(
                    partial(self.app.call_later, on_complete)
                    if on_complete is not None
                    else None
                ),
                level=level,
            )
        assert animation is not None, "animation expected to be non-None"

        current_animation = self._animations.get(animation_key)
        if current_animation is not None and current_animation == animation:
            return

        self._animations[animation_key] = animation
        self._timer.resume()
        self._idle_event.clear()
        self._complete_event.clear()

    async def _stop_scheduled_animation(
        self, key: AnimationKey, complete: bool
    ) -> None:
        """Stop a scheduled animation.

        Args:
            key: The key for the animation to stop.
            complete: Should the animation be moved to its completed state?
        """
        # First off, pull the timer out of the schedule and stop it; it
        # won't be needed.
        try:
            schedule = self._scheduled.pop(key)
        except KeyError:
            return
        schedule.stop()
        # If we've been asked to complete (there's no point in making the
        # animation only to then do nothing with it), and if there was a
        # callback (there will be, but this just keeps type checkers happy
        # really)...
        if complete and schedule._callback is not None:
            # ...invoke it to get the animator created and in the running
            # animations. Yes, this does mean that a stopped scheduled
            # animation will start running early...
            await invoke(schedule._callback)
            # ...but only so we can call on it to run right to the very end
            # right away.
            await self._stop_running_animation(key, complete)

    async def _stop_running_animation(self, key: AnimationKey, complete: bool) -> None:
        """Stop a running animation.

        Args:
            key: The key for the animation to stop.
            complete: Should the animation be moved to its completed state?
        """
        try:
            animation = self._animations.pop(key)
        except KeyError:
            return
        await animation.stop(complete)

    async def stop_animation(
        self, obj: object, attribute: str, complete: bool = True
    ) -> None:
        """Stop an animation on an attribute.

        Args:
            obj: The object containing the attribute.
            attribute: The name of the attribute.
            complete: Should the animation be set to its final value?

        Note:
            If there is no animation scheduled or running, this is a no-op.
        """
        key = (id(obj), attribute)
        if key in self._scheduled:
            await self._stop_scheduled_animation(key, complete)
        elif key in self._animations:
            await self._stop_running_animation(key, complete)

    def force_stop_animation(self, obj: object, attribute: str) -> None:
        """Force stop an animation on an attribute. This will immediately stop the animation,
        without running any associated callbacks, setting the attribute to its final value.

        Args:
            obj: The object containing the attribute.
            attribute: The name of the attribute.

        Note:
            If there is no animation scheduled or running, this is a no-op.
        """
        from .css.scalar_animation import ScalarAnimation

        animation_key = (id(obj), attribute)
        try:
            animation = self._animations.pop(animation_key)
        except KeyError:
            return

        if isinstance(animation, SimpleAnimation):
            setattr(obj, attribute, animation.end_value)
        elif isinstance(animation, ScalarAnimation):
            setattr(obj, attribute, animation.final_value)

        if animation.on_complete is not None:
            animation.on_complete()

    def __call__(self) -> None:
        if not self._animations:
            self._timer.pause()
            self._idle_event.set()
            if not self._scheduled:
                self._complete_event.set()
        else:
            app_animation_level = self.app.animation_level
            animation_time = self._get_time()
            animation_keys = list(self._animations.keys())
            for animation_key in animation_keys:
                animation = self._animations[animation_key]
                animation_complete = animation(animation_time, app_animation_level)
                if animation_complete:
                    del self._animations[animation_key]
                    if animation.on_complete is not None:
                        animation.on_complete()

    def _get_time(self) -> float:
        """Get the current wall clock time, via the internal Timer.

        Returns:
            The wall clock time.
        """
        # N.B. We could remove this method and always call `self._timer.get_time()` internally,
        # but it's handy to have in mocking situations.
        return _time.get_time()

    async def wait_for_idle(self) -> None:
        """Wait for any animations to complete."""
        await self._idle_event.wait()

    async def wait_until_complete(self) -> None:
        """Wait for any current and scheduled animations to complete."""
        await self._complete_event.wait()
