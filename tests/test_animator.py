from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from textual._animator import Animator, SimpleAnimation
from textual._easing import DEFAULT_EASING, EASING


class Animatable:
    """An animatable object."""

    def __init__(self, value):
        self.value = value

    def blend(self, destination: Animatable, factor: float) -> Animatable:
        return Animatable(self.value + (destination.value - self.value) * factor)


@dataclass
class AnimateTest:
    """An object with animatable properties."""

    foo: float | None = 0.0  # Plain float that may be set to None on final_value
    bar: Animatable = Animatable(0)  # A mock object supporting the animatable protocol


def test_simple_animation():
    """Test an animation from one float to another."""

    # Thing that may be animated
    animate_test = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animate_test,
        "foo",
        time,
        3.0,
        start_value=20.0,
        end_value=50.0,
        final_value=None,
        easing=lambda x: x,
    )

    assert animate_test.foo == 0.0

    assert animation(time) is False
    assert animate_test.foo == 20.0

    assert animation(time + 1.0) is False
    assert animate_test.foo == 30.0

    assert animation(time + 2.0) is False
    assert animate_test.foo == 40.0

    assert animation(time + 2.9) is False  # Not quite final value
    assert animate_test.foo == pytest.approx(49.0)

    assert animation(time + 3.0) is True  # True to indicate animation is complete
    assert animate_test.foo is None  # This is final_value

    assert animation(time + 3.0) is True
    assert animate_test.foo is None


def test_simple_animation_duration_zero():
    """Test animation handles duration of 0."""

    # Thing that may be animated
    animatable = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animatable,
        "foo",
        time,
        0.0,
        start_value=20.0,
        end_value=50.0,
        final_value=50.0,
        easing=lambda x: x,
    )

    assert animation(time) is True  # Duration is 0, so this is last value
    assert animatable.foo == 50.0

    assert animation(time + 1.0) is True
    assert animatable.foo == 50.0


def test_simple_animation_reverse():
    """Test an animation from one float to another, where the end value is less than the start."""

    # Thing that may be animated
    animate_Test = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animate_Test,
        "foo",
        time,
        3.0,
        start_value=50.0,
        end_value=20.0,
        final_value=20.0,
        easing=lambda x: x,
    )

    assert animation(time) is False
    assert animate_Test.foo == 50.0

    assert animation(time + 1.0) is False
    assert animate_Test.foo == 40.0

    assert animation(time + 2.0) is False
    assert animate_Test.foo == 30.0

    assert animation(time + 3.0) is True
    assert animate_Test.foo == 20.0


def test_animatable():
    """Test SimpleAnimation works with the Animatable protocol"""

    animate_test = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animate_test,
        "bar",
        time,
        3.0,
        start_value=Animatable(20.0),
        end_value=Animatable(50.0),
        final_value=Animatable(50.0),
        easing=lambda x: x,
    )

    assert animation(time) is False
    assert animate_test.bar.value == 20.0

    assert animation(time + 1.0) is False
    assert animate_test.bar.value == 30.0

    assert animation(time + 2.0) is False
    assert animate_test.bar.value == 40.0

    assert animation(time + 2.9) is False
    assert animate_test.bar.value == pytest.approx(49.0)

    assert animation(time + 3.0) is True  # True to indicate animation is complete
    assert animate_test.bar.value == 50.0


class MockAnimator(Animator):
    """A mock animator."""

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self._time = 0.0
        self._on_animation_frame_called = False

    def on_animation_frame(self):
        self._on_animation_frame_called = True

    def _get_time(self):
        return self._time


async def test_animator():
    target = Mock()
    animator = MockAnimator(target)
    animate_test = AnimateTest()

    # Animate attribute "foo" on animate_test to 100.0 in 10 seconds
    animator.animate(animate_test, "foo", 100.0, duration=10.0)

    expected = SimpleAnimation(
        animate_test,
        "foo",
        0.0,
        duration=10.0,
        start_value=0.0,
        end_value=100.0,
        final_value=100.0,
        easing=EASING[DEFAULT_EASING],
    )
    assert animator._animations[(id(animate_test), "foo")] == expected
    assert not animator._on_animation_frame_called

    await animator()
    assert animate_test.foo == 0

    animator._time = 5
    await animator()
    assert animate_test.foo == 50

    # New animation in the middle of an existing one
    animator.animate(animate_test, "foo", 200, duration=1)
    assert animate_test.foo == 50

    animator._time = 6
    await animator()
    assert animate_test.foo == 200


def test_bound_animator():
    target = Mock()
    animator = MockAnimator(target)
    animate_test = AnimateTest()

    # Bind an animator so it animates attributes on the given object
    bound_animator = animator.bind(animate_test)

    # Animate attribute "foo" on animate_test to 100.0 in 10 seconds
    bound_animator("foo", 100.0, duration=10)

    expected = SimpleAnimation(
        animate_test,
        "foo",
        0,
        duration=10,
        start_value=0,
        end_value=100,
        final_value=100,
        easing=EASING[DEFAULT_EASING],
    )
    assert animator._animations[(id(animate_test), "foo")] == expected


async def test_animator_on_complete_callback_not_fired_before_duration_ends():
    callback = Mock()
    animate_test = AnimateTest()
    animator = MockAnimator(Mock())

    animator.animate(animate_test, "foo", 200, duration=10, on_complete=callback)

    animator._time = 9
    await animator()

    assert not callback.called


async def test_animator_on_complete_callback_fired_at_duration():
    callback = Mock()
    animate_test = AnimateTest()
    animator = MockAnimator(Mock())

    animator.animate(animate_test, "foo", 200, duration=10, on_complete=callback)

    animator._time = 10
    await animator()

    callback.assert_called_once_with()
