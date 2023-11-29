from rich.style import Style
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

class HistoryTree(Tree):

    def __init__(self) -> None:
        super().__init__("Root")
        self.counter = 0
        self.render_hits: set[tuple[int, int]] = set()

    def on_mount(self) -> None:
        self.root.add("Child").add_leaf("Grandchild")

    def render_label(self, node: TreeNode, base_style: Style, style: Style) -> Text:
        self.render_hits.add((node.id, self.counter))
        return super().render_label(node, base_style, style)


class RefreshApp(App[None]):

    def compose(self) -> ComposeResult:
        yield HistoryTree()

    def on_mount(self) -> None:
        self.query_one(HistoryTree).root.expand_all()


async def test_initial_state() -> None:
    """Initially all the visible nodes should have had a render call."""
    app = RefreshApp()
    async with app.run_test():
        assert app.query_one(HistoryTree).render_hits == {(0,0), (1,0), (2,0)}


async def test_root_refresh() -> None:
    """A refresh of the root node should cause a subsequent render call."""
    async with RefreshApp().run_test() as pilot:
        assert (0, 1) not in pilot.app.query_one(HistoryTree).render_hits
        pilot.app.query_one(HistoryTree).counter += 1
        pilot.app.query_one(HistoryTree).root.refresh()
        await pilot.pause()
        assert (0, 1) in pilot.app.query_one(HistoryTree).render_hits

async def test_child_refresh() -> None:
    """A refresh of the child node should cause a subsequent render call."""
    async with RefreshApp().run_test() as pilot:
        assert (1, 1) not in pilot.app.query_one(HistoryTree).render_hits
        pilot.app.query_one(HistoryTree).counter += 1
        pilot.app.query_one(HistoryTree).root.children[0].refresh()
        await pilot.pause()
        assert (1, 1) in pilot.app.query_one(HistoryTree).render_hits

async def test_grandchild_refresh() -> None:
    """A refresh of the grandchild node should cause a subsequent render call."""
    async with RefreshApp().run_test() as pilot:
        assert (2, 1) not in pilot.app.query_one(HistoryTree).render_hits
        pilot.app.query_one(HistoryTree).counter += 1
        pilot.app.query_one(HistoryTree).root.children[0].children[0].refresh()
        await pilot.pause()
        assert (2, 1) in pilot.app.query_one(HistoryTree).render_hits
