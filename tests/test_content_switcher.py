from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import ContentSwitcher


class SwitcherApp(App[None]):
    def __init__(self, initial: str | None = None) -> None:
        super().__init__()
        self._initial = initial

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial=self._initial):
            for n in range(5):
                yield Widget(id=f"w{n}")


async def test_no_initial_display() -> None:
    """Test starting a content switcher with nothing shown."""
    async with SwitcherApp().run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current is None
        assert all(
            not child.display for child in pilot.app.query_one(ContentSwitcher).children
        )
        assert pilot.app.query_one(ContentSwitcher).visible_content is None


async def test_initial_display() -> None:
    """Test starting a content switcher with a widget initially shown."""
    async with SwitcherApp("w3").run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current == "w3"
        for child in pilot.app.query_one(ContentSwitcher).children:
            assert child.display is (child.id == "w3")
        assert pilot.app.query_one(
            ContentSwitcher
        ).visible_content is pilot.app.query_one("#w3")


async def test_no_initial_display_then_set() -> None:
    """Test starting a content switcher with nothing shown then setting the display."""
    async with SwitcherApp().run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current is None
        assert all(
            not child.display for child in pilot.app.query_one(ContentSwitcher).children
        )
        assert pilot.app.query_one(ContentSwitcher).visible_content is None
        pilot.app.query_one(ContentSwitcher).current = "w3"
        assert pilot.app.query_one(ContentSwitcher).current == "w3"
        for child in pilot.app.query_one(ContentSwitcher).children:
            assert child.display is (child.id == "w3")
        assert pilot.app.query_one(
            ContentSwitcher
        ).visible_content is pilot.app.query_one("#w3")


async def test_initial_display_then_change() -> None:
    """Test starting a content switcher with a widget initially shown then changing it."""
    async with SwitcherApp("w3").run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current == "w3"
        for child in pilot.app.query_one(ContentSwitcher).children:
            assert child.display is (child.id == "w3")
        assert pilot.app.query_one(
            ContentSwitcher
        ).visible_content is pilot.app.query_one("#w3")
        pilot.app.query_one(ContentSwitcher).current = "w2"
        assert pilot.app.query_one(ContentSwitcher).current == "w2"
        for child in pilot.app.query_one(ContentSwitcher).children:
            assert child.display is (child.id == "w2")
        assert pilot.app.query_one(
            ContentSwitcher
        ).visible_content is pilot.app.query_one("#w2")


async def test_initial_display_then_hide() -> None:
    """Test starting a content switcher with a widget initially shown then hide all."""
    async with SwitcherApp("w3").run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current == "w3"
        for child in pilot.app.query_one(ContentSwitcher).children:
            assert child.display is (child.id == "w3")
        pilot.app.query_one(ContentSwitcher).current = None
        assert pilot.app.query_one(ContentSwitcher).current is None
        assert all(
            not child.display for child in pilot.app.query_one(ContentSwitcher).children
        )


@pytest.mark.xfail(
    reason="The expected exception doesn't appear to make it to pytest -- perhaps related to https://github.com/Textualize/textual/issues/1972"
)
async def test_initial_display_unknown_id() -> None:
    """Test setting an initial display to an unknown widget ID."""
    with pytest.raises(NoMatches):
        async with SwitcherApp("does-not-exist").run_test():
            pass


async def test_set_current_to_unknown_id() -> None:
    """Test attempting to switch to an unknown widget ID."""
    async with SwitcherApp().run_test() as pilot:
        assert pilot.app.query_one(ContentSwitcher).current is None
        assert all(
            not child.display for child in pilot.app.query_one(ContentSwitcher).children
        )
        with pytest.raises(NoMatches):
            pilot.app.query_one(ContentSwitcher).current = "does-not-exist"
