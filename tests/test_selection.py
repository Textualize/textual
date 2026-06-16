import pytest

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.geometry import Offset
from textual.selection import Selection
from textual.widgets import Static


@pytest.mark.parametrize(
    "text,selection,expected",
    [
        ("Hello", Selection(None, None), "Hello"),
        ("Hello\nWorld", Selection(None, None), "Hello\nWorld"),
        ("Hello\nWorld", Selection(Offset(0, 1), None), "World"),
        ("Hello\nWorld", Selection(None, Offset(5, 0)), "Hello"),
        ("Foo", Selection(Offset(0, 0), Offset(1, 0)), "F"),
        ("Foo", Selection(Offset(1, 0), Offset(2, 0)), "o"),
        ("Foo", Selection(Offset(0, 0), Offset(2, 0)), "Fo"),
        ("Foo", Selection(Offset(0, 0), None), "Foo"),
    ],
)
def test_extract(text: str, selection: Selection, expected: str) -> None:
    """Test Selection.extract"""
    assert selection.extract(text) == expected


async def test_double_width():
    """Test that selection works with double width characters."""

    TEXT = """😂❤️👍Select😊🙏😍\nme🔥💯😭😂❤️👍"""

    class TextSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static(TEXT)

    app = TextSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert await pilot.mouse_down(offset=(2, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(7, 1))
        selected_text = app.screen.get_selected_text()
        expected = "❤️👍Select😊🙏😍\nme🔥💯😭😂"

    assert selected_text == expected


class _ScrollableSelectApp(App):
    """Test app: 'BEFORE' / scrollable container with 10 items / 'AFTER'."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #before, #after, .item {
        height: 1;
    }
    #scroller {
        height: 5;
        border: none;
        padding: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("BEFORE", id="before")
        with VerticalScroll(id="scroller"):
            for i in range(10):
                yield Static(f"item-{i:02d}", classes="item", id=f"item-{i}")
        yield Static("AFTER", id="after")


async def test_select_into_scrollable_container():
    """Selecting from outside (above) into a scrollable container should pick up
    items scrolled above the visible area."""

    app = _ScrollableSelectApp()
    async with app.run_test(size=(20, 10)) as pilot:
        await pilot.pause()
        scroller = app.query_one("#scroller", VerticalScroll)
        # Scroll so items 00-02 are scrolled above the visible area.
        scroller.scroll_to(y=3, animate=False)
        await pilot.pause()

        # Selection: start on "BEFORE" (y=0), end inside the container on the
        # last visible row.
        assert await pilot.mouse_down(offset=(0, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(7, 5))
        selected_text = app.screen.get_selected_text() or ""

        assert "BEFORE" in selected_text
        for i in range(0, 7):
            assert (
                f"item-{i:02d}" in selected_text
            ), f"item-{i:02d} missing from {selected_text!r}"
        assert "AFTER" not in selected_text


async def test_select_out_of_scrollable_container():
    """Selecting from inside a scrollable container to outside (below) should
    pick up items scrolled below the visible area."""

    app = _ScrollableSelectApp()
    async with app.run_test(size=(20, 10)) as pilot:
        await pilot.pause()
        # Default scroll: items 05-09 are scrolled below the visible area.
        scroller = app.query_one("#scroller", VerticalScroll)
        assert scroller.scroll_y == 0

        # Selection: start inside the container at top row, end below on "AFTER".
        assert await pilot.mouse_down(offset=(0, 1))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(0, 7))
        selected_text = app.screen.get_selected_text() or ""

        for i in range(0, 10):
            assert (
                f"item-{i:02d}" in selected_text
            ), f"item-{i:02d} missing from {selected_text!r}"
        assert "AFTER" in selected_text
        assert "BEFORE" not in selected_text


async def test_select_across_scrollable_container():
    """Selecting from outside (above) to outside (below) of a scrollable
    container should select all of its content."""

    app = _ScrollableSelectApp()
    async with app.run_test(size=(20, 10)) as pilot:
        await pilot.pause()
        scroller = app.query_one("#scroller", VerticalScroll)
        scroller.scroll_to(y=2, animate=False)
        await pilot.pause()

        # Selection: BEFORE (y=0) to AFTER (y=7).
        assert await pilot.mouse_down(offset=(0, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(0, 7))
        selected_text = app.screen.get_selected_text() or ""

        assert "BEFORE" in selected_text
        assert "AFTER" in selected_text
        for i in range(0, 10):
            assert (
                f"item-{i:02d}" in selected_text
            ), f"item-{i:02d} missing from {selected_text!r}"


class _GappedScrollApp(App):
    """A scrollable container whose items have a 1-row gap between them, so
    moving the mouse across the container crosses non-content rows."""

    CSS = """
    Screen { layout: vertical; }
    #before, #after { height: 1; }
    .item {
        height: 1;
        margin-bottom: 1;
    }
    #scroller {
        height: 7;
        border: none;
        padding: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("BEFORE", id="before")
        with VerticalScroll(id="scroller"):
            for i in range(8):
                yield Static(f"item-{i:02d}", classes="item", id=f"item-{i}")
        yield Static("AFTER", id="after")


async def test_select_into_scrollable_container_on_gap():
    """Regression: when the end pointer lands on a gap (margin row) inside a
    scrollable container, the selection should extend only to widgets at or
    above that pointer row — not to every widget in the container, which caused
    a flashing selection as the user moved between content widgets."""

    app = _GappedScrollApp()
    async with app.run_test(size=(20, 12)) as pilot:
        await pilot.pause()

        # Layout: BEFORE y=0, scroller y=1..7, items at y=1 (item-0), y=3
        # (item-1), y=5 (item-2), y=7 (item-3). Margin rows y=2, 4, 6.
        # mouse_down on BEFORE, mouse_up at y=2 (gap between item-0 and item-1).
        assert await pilot.mouse_down(offset=(0, 0))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(0, 2))
        selected_text = app.screen.get_selected_text() or ""

        assert "BEFORE" in selected_text
        assert "item-00" in selected_text
        # item-01 onward are below the gap — should NOT be selected.
        for i in range(1, 8):
            assert (
                f"item-{i:02d}" not in selected_text
            ), f"item-{i:02d} should not be in {selected_text!r}"


async def test_select_out_of_scrollable_container_on_gap():
    """Regression: when the start pointer is on a gap (margin row) inside a
    scrollable container and the user drags out below, only widgets at or
    below the pointer row should be selected."""

    app = _GappedScrollApp()
    async with app.run_test(size=(20, 12)) as pilot:
        await pilot.pause()

        # mouse_down at y=2 (gap between item-0 and item-1). mouse_up inside
        # AFTER's text (col 5 of "AFTER" -> just past the last char).
        assert await pilot.mouse_down(offset=(0, 2))
        await pilot.pause()
        assert await pilot.mouse_up(offset=(5, 8))
        selected_text = app.screen.get_selected_text() or ""

        assert "AFTER" in selected_text
        # item-0 is above the start gap row — should NOT be selected.
        assert "item-00" not in selected_text
        # item-01 onward are below the start gap row — should be selected.
        for i in range(1, 8):
            assert (
                f"item-{i:02d}" in selected_text
            ), f"item-{i:02d} missing from {selected_text!r}"
