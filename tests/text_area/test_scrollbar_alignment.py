from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Tree, OptionList
from textual.containers import VerticalScroll


class ScrollBarLocationApp(App[None]):
    CSS = """
    Screen > * {
        width: 1fr;
        height: 1fr;
        border: none;
        background: $surface;
        &:focus {
            background: $panel;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield TextArea(id="ta")
        yield Tree("", id="tree")
        yield OptionList(id="ol")
        yield VerticalScroll(id="vs")

    def on_mount(self) -> None:
        self.query_one(TextArea).load_text("\n".join(f"This is line {n}" for n in range(100)))
        self.query_one(Tree).root.expand()
        for n in range(100):
            self.query_one(Tree).root.add(f"This is node {n}")
        self.query_one(OptionList).add_options(f"This is option {n}" for n in range(100))
        self.query_one("#vs").mount_all(
            *(self._make_label(n) for n in range(100))
        )

    def _make_label(self, n: int):
        # Avoid importing Label directly to keep dependencies minimal
        from textual.widgets import Static
        return Static(f"This is label {n}")


@pytest.mark.asyncio
async def test_vertical_scrollbar_alignment(snapshot):
    """Assert that TextArea's vertical scrollbar aligns with other widgets' scrollbars.

    The alignment heuristic used here: when all widgets have vertical scrollbars visible,
    their rightmost x coordinate (including border/gutter) should be identical.
    """
    app = ScrollBarLocationApp()

    async with app.run_test() as pilot:
        # Ensure widgets mounted and layout settled
        await pilot.pause(0.1)

        ta = app.query_one("#ta")
        tree = app.query_one("#tree")
        ol = app.query_one("#ol")
        vs = app.query_one("#vs")

        # Force scrollbars to be shown by ensuring content exceeds viewport
        assert ta.show_vertical_scrollbar
        assert tree.show_vertical_scrollbar
        assert ol.show_vertical_scrollbar
        assert vs.show_vertical_scrollbar

        # Compare right edges in screen coordinates
        right_edges = [w.region.right for w in (ta, tree, ol, vs)]
        # All right edges should be equal (i.e., scrollbars aligned to same gutter)
        assert len(set(right_edges)) == 1
