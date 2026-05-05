"""Tests for word and line selection granularity (SelectionMode.STANDARD)."""

import pytest

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.selection import SelectionMode
from textual.widgets import Static


class WordLineSelectApp(App):
    """App with SelectionMode.STANDARD for word/line selection."""

    SELECTION_MODE = SelectionMode.STANDARD

    def compose(self) -> ComposeResult:
        yield Static("Hello World\nfoo bar baz\nline three here", id="text")


class LegacySelectApp(App):
    """App with SelectionMode.LEGACY (default, select-all behavior)."""

    def compose(self) -> ComposeResult:
        yield Static("Hello World\nfoo bar baz", id="text")


async def test_selection_mode_default_is_legacy():
    """SELECTION_MODE defaults to SelectionMode.LEGACY."""
    app = LegacySelectApp()
    assert app.SELECTION_MODE == SelectionMode.LEGACY


async def test_double_click_does_not_select_all_in_standard_mode():
    """With SelectionMode.STANDARD, double-click should NOT select all text."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Double-click on a word
        await pilot.click(offset=(2, 0), times=2)
        await pilot.pause()
        # Widget._on_click should NOT call text_select_all
        # The screen's selection should be set by the granularity system instead
        selected = app.screen.get_selected_text()
        # Should NOT have selected all text in the widget
        if selected is not None:
            assert selected != "Hello World\nfoo bar baz\nline three here"


async def test_word_at_offset_basic():
    """Test Widget.word_at_offset returns correct word boundaries."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # "Hello" starts at x=0, ends at x=5
        result = widget.word_at_offset(Offset(2, 0))
        assert result is not None
        start, end = result
        assert start == Offset(0, 0)
        assert end == Offset(5, 0)


async def test_word_at_offset_second_word():
    """Test word_at_offset for a word not at start of line."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # "World" starts at x=6, ends at x=11
        result = widget.word_at_offset(Offset(8, 0))
        assert result is not None
        start, end = result
        assert start == Offset(6, 0)
        assert end == Offset(11, 0)


async def test_word_at_offset_on_space_returns_none():
    """Test word_at_offset returns None when clicking on a space."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # Space between "Hello" and "World" at x=5
        result = widget.word_at_offset(Offset(5, 0))
        assert result is None


async def test_word_at_offset_second_line():
    """Test word_at_offset works on non-first lines."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # "bar" on line 1 starts at x=4, ends at x=7
        result = widget.word_at_offset(Offset(5, 1))
        assert result is not None
        start, end = result
        assert start == Offset(4, 1)
        assert end == Offset(7, 1)


async def test_line_at_offset_basic():
    """Test Widget.line_at_offset returns correct line boundaries."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # First line: "Hello World" (11 chars)
        result = widget.line_at_offset(Offset(3, 0))
        assert result is not None
        start, end = result
        assert start == Offset(0, 0)
        assert end == Offset(11, 0)


async def test_line_at_offset_second_line():
    """Test line_at_offset on second line."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        # Second line: "foo bar baz" (11 chars)
        result = widget.line_at_offset(Offset(5, 1))
        assert result is not None
        start, end = result
        assert start == Offset(0, 1)
        assert end == Offset(11, 1)


async def test_word_at_offset_out_of_bounds():
    """Test word_at_offset returns None for out-of-bounds offsets."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        assert widget.word_at_offset(Offset(0, 99)) is None
        assert widget.word_at_offset(Offset(99, 0)) is None
        assert widget.word_at_offset(Offset(-1, 0)) is None


async def test_line_at_offset_out_of_bounds():
    """Test line_at_offset returns None for out-of-bounds offsets."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#text")
        assert widget.line_at_offset(Offset(0, 99)) is None
        assert widget.line_at_offset(Offset(0, -1)) is None


async def test_double_click_selects_word():
    """Double-click selects a word (standard terminal behavior)."""
    app = WordLineSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # First click
        assert await pilot.mouse_down(offset=(8, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(8, 0))
        await pilot.pause()
        # Second click (double-click) — triggers word selection
        assert await pilot.mouse_down(offset=(8, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(8, 0))
        await pilot.pause()
        selected = app.screen.get_selected_text()
        assert selected == "World"


async def test_legacy_double_click_selects_all():
    """With SELECTION_MODE=False, double-click selects entire widget (legacy behavior)."""
    app = LegacySelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # pilot.click with times=2 triggers Widget._on_click with chain=2
        await pilot.click(offset=(2, 0), times=2)
        await pilot.pause()
        selected = app.screen.get_selected_text()
        # Default behavior: should select all text in the widget
        assert selected == "Hello World\nfoo bar baz"


async def test_triple_click_selects_line():
    """Triple-click selects the full visual line."""
    app = WordLineSelectApp()
    async with app.run_test(size=(80, 5)) as pilot:
        await pilot.pause()
        w = app.query_one("#text")
        x = w.region.x + 2
        y = w.region.y + 1  # Second line: "foo bar baz"
        # Triple click
        await pilot.mouse_down(offset=(x, y))
        await pilot.mouse_up(offset=(x, y))
        await pilot.mouse_down(offset=(x, y))
        await pilot.mouse_up(offset=(x, y))
        await pilot.mouse_down(offset=(x, y))
        await pilot.mouse_up(offset=(x, y))
        await pilot.pause()
        selected = app.screen.get_selected_text()
        assert selected == "foo bar baz"


class TwoWidgetApp(App):
    """App with a TextArea and a Static to test clear_selection interaction."""

    SELECTION_MODE = SelectionMode.STANDARD

    def compose(self) -> ComposeResult:
        from textual.widgets import TextArea

        yield TextArea("input text", id="input")
        yield Static("Hello World\nfoo bar baz", id="text")


async def test_clear_selection_preserves_granularity_during_click_chain():
    """When another widget calls clear_selection during a double-click,
    the click chain granularity must not be reset.

    This was a real bug: TextArea._watch_selection calls app.clear_selection()
    when focus changes, which wiped the granularity set by the MouseDown handler.
    """
    app = TwoWidgetApp()
    async with app.run_test(size=(80, 10)) as pilot:
        await pilot.pause()
        text_widget = app.query_one("#text")
        x = text_widget.region.x + 2
        y = text_widget.region.y
        # First click (may trigger TextArea focus change → clear_selection)
        await pilot.mouse_down(offset=(x, y))
        await pilot.mouse_up(offset=(x, y))
        # Second click (double-click → should select word despite clear_selection)
        await pilot.mouse_down(offset=(x, y))
        # Granularity should survive any clear_selection calls
        assert app.screen._select_granularity == "word", (
            f"Expected granularity 'word' but got '{app.screen._select_granularity}'"
        )
        await pilot.mouse_up(offset=(x, y))
        await pilot.pause()
        selected = app.screen.get_selected_text()
        assert selected == "Hello"


async def test_double_click_drag_selects_word_by_word():
    """Double-click and drag should extend selection word-by-word."""
    app = WordLineSelectApp()
    async with app.run_test(size=(80, 5)) as pilot:
        await pilot.pause()
        w = app.query_one("#text")
        # Double-click on "Hello" (x=2)
        x_start = w.region.x + 2
        y = w.region.y
        await pilot.mouse_down(offset=(x_start, y))
        await pilot.mouse_up(offset=(x_start, y))
        await pilot.mouse_down(offset=(x_start, y))
        # Now drag to "World" (x=8)
        x_end = w.region.x + 8
        await pilot.hover(offset=(x_end, y))
        await pilot.pause()
        selected = app.screen.get_selected_text()
        # Should have selected both words, not just characters
        assert selected is not None
        assert "Hello" in selected
        assert "World" in selected
        await pilot.mouse_up(offset=(x_end, y))
