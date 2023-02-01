from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Tree


class VerseBody:
    pass


class VerseStar(VerseBody):
    pass


class VersePlanet(VerseBody):
    pass


class VerseMoon(VerseBody):
    pass


class TestTree(Tree[VerseBody]):
    pass


class TreeClearApp(App[None]):
    """Tree clearing test app."""

    def compose(self) -> ComposeResult:
        yield TestTree("White Sun", data=VerseStar())

    def on_mount(self) -> None:
        tree = self.query_one(TestTree)
        node = tree.root.add("Londinium", VersePlanet())
        node.add_leaf("Balkerne", VerseMoon())
        node.add_leaf("Colchester", VerseMoon())
        node = tree.root.add("Sihnon", VersePlanet())
        node.add_leaf("Airen", VerseMoon())
        node.add_leaf("Xiaojie", VerseMoon())


async def test_tree_simple_clear() -> None:
    """Clearing a tree should keep the old label and data."""
    async with TreeClearApp().run_test() as pilot:
        tree = pilot.app.query_one(TestTree)
        assert len(tree.root.children) > 1
        pilot.app.query_one(TestTree).clear()
        assert len(tree.root.children) == 0
        assert str(tree.root.label) == "White Sun"
        assert isinstance(tree.root.data, VerseStar)


async def test_tree_new_label_clear() -> None:
    """Clearing a tree with a new label should use the new label and keep the old data."""
    async with TreeClearApp().run_test() as pilot:
        tree = pilot.app.query_one(TestTree)
        assert len(tree.root.children) > 1
        pilot.app.query_one(TestTree).clear("Jiangyin")
        assert len(tree.root.children) == 0
        assert str(tree.root.label) == "Jiangyin"
        assert isinstance(tree.root.data, VerseStar)
