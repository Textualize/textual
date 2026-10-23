"""
Tests for the tabs underline animation, which is considered a basic animation.
(An animation that also plays on the level BASIC.)
"""

import asyncio

import pytest

from textual.app import App, ComposeResult
from textual.types import AnimationLevel
from textual.widgets import Label, TabbedContent, Tabs


class TabbedContentApp(App[None]):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            for _ in range(10):
                yield Label("Hey!")


@pytest.mark.parametrize("animation_level", ["full", "basic"])
async def test_tabs_underline_animates(animation_level: AnimationLevel) -> None:
    """The underline takes some time to move when animated."""
    app = TabbedContentApp()
    app.animation_level = animation_level

    animations: list[str] = []
    animation_recorded = asyncio.Event()

    def record_animation(attribute: str) -> None:
        animations.append(attribute)
        if attribute == "highlight_end":
            animation_recorded.set()

    async with app.run_test() as pilot:
        await pilot.pause()
        app.animator._record_animation = record_animation
        app.query_one(Tabs).action_previous_tab()
        # Tabs starts its underline animation from a delayed timer, so waiting
        # for idle alone may return before the animation is scheduled.
        await asyncio.wait_for(animation_recorded.wait(), timeout=5)
        assert "highlight_start" in animations
        assert "highlight_end" in animations


async def test_tabs_underline_does_not_animate_on_none() -> None:
    """The underline jumps to its final position when not animated."""
    app = TabbedContentApp()
    app.animation_level = "none"

    animations: list[str] = []

    async with app.run_test() as pilot:
        animator = app.animator
        animator._record_animation = animations.append
        app.query_one(Tabs).action_previous_tab()
        await pilot.pause()
        assert "highlight_start" not in animations
        assert "highlight_end" not in animations
