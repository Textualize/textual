import asyncio
import gc

import pytest

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Label


def count_nodes() -> int:
    """Count number of references to DOMNodes."""
    dom_nodes = [
        obj
        for obj in gc.get_objects()
        if any(cls.__name__ == "DOMNode" for cls in obj.__class__.__mro__)
    ]
    print(dom_nodes)
    return len(dom_nodes)


async def run_app() -> None:
    """Run a dummy app."""

    class DummyApp(App):
        """Dummy app with a few widgets."""

        def compose(self) -> ComposeResult:
            yield Header()
            with Vertical():
                yield Label("foo")
                yield Label("bar")
            yield Footer()

    app = DummyApp()

    async with app.run_test() as pilot:
        # We should have a bunch of DOMNodes while the test is running
        assert count_nodes() > 0
        await pilot.press("ctrl+c")

    assert not app._running

    # Force a GC collection
    gc.collect()

    # After the test, all DOMNodes will have been torn down
    assert count_nodes() == 1


async def _count_app_nodes() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4959"""

    # Should be no DOMNodes yet
    assert count_nodes() == 0

    await run_app()
    await asyncio.sleep(0)

    gc.collect()

    nodes_remaining = count_nodes()

    if nodes_remaining:
        print("NODES REMAINING")

        import objgraph

        objgraph.show_backrefs(
            [
                obj
                for obj in gc.get_objects()
                if any(cls.__name__ == "App" for cls in obj.__class__.__mro__)
            ],
            filename="graph.png",
            max_depth=15,
        )

    assert nodes_remaining == 0


# It looks like PyTest holds on to references to DOMNodes
# So this will only pass if ran in isolation
@pytest.mark.xfail
async def test_gc():
    """Regression test for https://github.com/Textualize/textual/issues/4959"""
    await _count_app_nodes()
