"""Tests for exceptions thrown by the Dialog widget."""

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Dialog, Label


class MultipleActionAreasApp(App[None]):
    def compose(self) -> ComposeResult:
        with Dialog():
            yield Label("Test")
            with Dialog.ActionArea():
                yield Label("One")
            with Dialog.ActionArea():
                yield Label("Two")


async def test_too_many_action_areas() -> None:
    """More than one dialog action area should result in an error."""
    with pytest.raises(Dialog.TooManyActionAreas):
        async with MultipleActionAreasApp().run_test():
            pass


class MisplacedActionAreaApp(App[None]):
    def compose(self) -> ComposeResult:
        with Dialog.ActionArea():
            yield Label("This should not be alone")


async def test_misplaced_action_area() -> None:
    """Test that an exception is raised if an action area is misplaced."""
    with pytest.raises(Dialog.MisplacedActionArea):
        async with MisplacedActionAreaApp().run_test():
            pass


class MisplacedActionAreaGroupApp(App[None]):
    def compose(self) -> ComposeResult:
        with Dialog.ActionArea.GroupLeft():
            yield Label("This should not be alone")


async def test_misplaced_action_area_group() -> None:
    """Test that an exception is raised if an action area group is misplaced."""
    with pytest.raises(Dialog.MisplacedActionGroup):
        async with MisplacedActionAreaGroupApp().run_test():
            pass
