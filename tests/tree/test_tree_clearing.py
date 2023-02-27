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


class VerseTree(Tree[VerseBody]):
    pass


class TreeClearApp(App[None]):
    """Tree clearing test app."""

    def compose(self) -> ComposeResult:
        yield VerseTree("White Sun", data=VerseStar())

    def on_mount(self) -> None:
        tree = self.query_one(VerseTree)
        node = tree.root.add("Londinium", VersePlanet())
        node.add_leaf("Balkerne", VerseMoon())
        node.add_leaf("Colchester", VerseMoon())
        node = tree.root.add("Sihnon", VersePlanet())
        node.add_leaf("Airen", VerseMoon())
        node.add_leaf("Xiaojie", VerseMoon())


async def test_tree_simple_clear() -> None:
    """Clearing a tree should keep the old root label and data."""
    async with TreeClearApp().run_test() as pilot:
        tree = pilot.app.query_one(VerseTree)
        assert len(tree.root.children) > 1
        pilot.app.query_one(VerseTree).clear()
        assert len(tree.root.children) == 0
        assert str(tree.root.label) == "White Sun"
        assert isinstance(tree.root.data, VerseStar)


async def test_tree_reset_with_label() -> None:
    """Resetting a tree with a new label should use the new label and set the data to None."""
    async with TreeClearApp().run_test() as pilot:
        tree = pilot.app.query_one(VerseTree)
        assert len(tree.root.children) > 1
        pilot.app.query_one(VerseTree).reset(label="Jiangyin")
        assert len(tree.root.children) == 0
        assert str(tree.root.label) == "Jiangyin"
        assert tree.root.data is None


async def test_tree_reset_with_label_and_data() -> None:
    """Resetting a tree with a label and data have that label and data used."""
    async with TreeClearApp().run_test() as pilot:
        tree = pilot.app.query_one(VerseTree)
        assert len(tree.root.children) > 1
        pilot.app.query_one(VerseTree).reset(label="Jiangyin", data=VersePlanet())
        assert len(tree.root.children) == 0
        assert str(tree.root.label) == "Jiangyin"
        assert isinstance(tree.root.data, VersePlanet)
