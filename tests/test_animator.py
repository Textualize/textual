from __future__ import annotations


from dataclasses import dataclass
from unittest.mock import Mock

import pytest


from textual._animator import SimpleAnimation


class Animatable:
    """An animatable object."""

    def __init__(self, value):
        self.value = value

    def blend(self, destination: Animatable, factor: float) -> Animatable:
        return Animatable(self.value + (destination.value - self.value) * factor)


@dataclass
class AnimateTest:
    """An object to animate."""

    foo: float | None = 0  # Plain float that may be set to None on final_value
    bar: Animatable = Animatable(0)  # A mock object supporting the animatable protocol


def test_simple_animation():
    """Test an animation from one float to another."""

    # Thing that may be animated
    animatable = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animatable,
        "foo",
        time,
        3.0,
        start_value=20.0,
        end_value=50.0,
        final_value=None,
        easing=lambda x: x,
    )

    assert animation(time) is False
    assert animatable.foo == 20.0

    assert animation(time + 1.0) is False
    assert animatable.foo == 30.0

    assert animation(time + 2.0) is False
    assert animatable.foo == 40.0

    assert animation(time + 2.9) is False
    assert pytest.approx(animatable.foo, 49.0)

    assert animation(time + 3.0) is True  # True to indicate animation is complete
    assert animatable.foo is None  # This is final_value

    assert animation(time + 3.0) is True
    assert animatable.foo is None


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

    assert animation(time) is True
    assert animatable.foo == 50.0

    assert animation(time + 1.0) is True
    assert animatable.foo == 50.0


def test_simple_animation_reverse():
    """Test an animation from one float to another, where the end value is less than the start."""

    # Thing that may be animated
    animatable = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animatable,
        "foo",
        time,
        3.0,
        start_value=50.0,
        end_value=20.0,
        final_value=20.0,
        easing=lambda x: x,
    )

    assert animation(time) is False
    assert animatable.foo == 50.0

    assert animation(time + 1.0) is False
    assert animatable.foo == 40.0

    assert animation(time + 2.0) is False
    assert animatable.foo == 30.0

    assert animation(time + 3.0) is True
    assert animatable.foo == 20.0


def test_animatable():
    """Test SimpleAnimation works with the Animatable protocol"""

    animatable = AnimateTest()

    # Fake wall-clock time
    time = 100.0

    # Object that does the animation
    animation = SimpleAnimation(
        animatable,
        "bar",
        time,
        3.0,
        start_value=Animatable(20.0),
        end_value=Animatable(50.0),
        final_value=Animatable(50.0),
        easing=lambda x: x,
    )

    assert animation(time) is False
    assert animatable.bar.value == 20.0

    assert animation(time + 1.0) is False
    assert animatable.bar.value == 30.0

    assert animation(time + 2.0) is False
    assert animatable.bar.value == 40.0

    assert animation(time + 2.9) is False
    assert pytest.approx(animatable.bar.value, 49.0)

    assert animation(time + 3.0) is True  # True to indicate animation is complete
    assert animatable.bar.value == 50.0
