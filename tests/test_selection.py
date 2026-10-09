import pytest

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
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


async def test_double_click_selects_word():
    """Double-clicking a word should select just that word."""

    class WordSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static("hello world foo bar")

    app = WordSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one(Static)
        await pilot.click(static, offset=(8, 0), times=2)
        await pilot.pause()
        assert app.screen.get_selected_text() == "world"


async def test_double_click_selects_url():
    """Double-clicking inside a URL should select the whole URL."""

    class UrlSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static("Visit https://example.com/path for info.")

    app = UrlSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one(Static)
        await pilot.click(static, offset=(18, 0), times=2)
        await pilot.pause()
        assert app.screen.get_selected_text() == "https://example.com/path"


async def test_triple_click_selects_paragraph():
    """Triple-clicking should select the paragraph at the click location."""

    class ParagraphSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static("first paragraph\n\nsecond paragraph\nmore text")

    app = ParagraphSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one(Static)
        await pilot.click(static, offset=(2, 3), times=3)
        await pilot.pause()
        assert app.screen.get_selected_text() == "second paragraph\nmore text"


async def test_double_click_clears_select_state():
    """Double-clicking a word should leave the selection state consistent."""

    class WordSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Static("hello world foo bar")

    app = WordSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one(Static)
        await pilot.click(static, offset=(8, 0), times=2)
        await pilot.pause()
        assert app.screen.get_selected_text() == "world"
        assert app.screen._select_state is None


async def test_triple_click_fallback_selects_container():
    """Triple-clicking a non-text widget should select its container."""

    from textual.renderables.blank import Blank

    class NonTextWidget(Static):
        def render(self) -> Blank:
            return Blank()

    class ContainerSelectApp(App):
        def compose(self) -> ComposeResult:
            with VerticalScroll(id="container"):
                yield NonTextWidget()

    app = ContainerSelectApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one(NonTextWidget)
        container = widget.select_container
        await pilot.click(widget, times=3)
        await pilot.pause()
        assert app.screen.selections.get(container) is not None


async def test_get_selectable_text_shared_with_get_selection():
    """get_selectable_text should return the text that get_selection extracts from."""

    class SelectableTextApp(App):
        def compose(self) -> ComposeResult:
            yield Static("hello world")

    app = SelectableTextApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one(Static)
        text = static.get_selectable_text()
        selection = static.get_selection(Selection.from_offsets(Offset(6, 0), Offset(11, 0)))
        assert text == "hello world"
        assert selection == ("world", "\n")
