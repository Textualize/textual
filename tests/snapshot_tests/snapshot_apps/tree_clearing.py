from textual.app import App, ComposeResult
from textual.widgets import Tree

class TreeClearingSnapshotApp(App[None]):

    CSS = """
    Screen {
        layout: horizontal;
    }
    """

    @staticmethod
    def _populate(tree: Tree) -> Tree:
        for n in range(5):
            branch = tree.root.add(str(n))
            for m in range(5):
                branch.add_leaf(f"{n}-{m}")
        return tree

    def compose(self) -> ComposeResult:
        yield self._populate(Tree("Left", id="left"))
        yield self._populate(Tree("Right", id="right"))

    def on_mount(self) -> None:
        self.query_one("#left", Tree).root.expand()
        self.query_one("#left", Tree).clear()
        self.query_one("#right", Tree).clear()

if __name__ == "__main__":
    TreeClearingSnapshotApp().run()
