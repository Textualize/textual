"""Support for subclassing Tree."""

from rich.style import Style
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import Button, Tree
from textual.widgets.tree import TreeNode

import textual


class MyTree(Tree):
    """Subclass of Tree."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_counter = 0
        self.render_history: set[str] = set()

    def render_label(
        self, node: TreeNode, base_style: Style, style: Style
    ) -> Text:
        """Render nodes to include the test_counter."""
        node_label = node._label.copy()
        node_label.stylize(style)
        prefix = (f'{self.test_counter} ', base_style)
        text = Text.assemble(prefix, node_label)
        self.render_history.add(text.plain)
        return text


class TreeApp(App[None]):
    """Test tree app.

    This has a simple tree that looks like this:

    ```
        0 Test
        ┗━━ 0 Branch
            ┗━━ 0 Leaf
    ```

    The leading numbers are the value of `test_counter` the last time that
    the node was rendered.

    The application also has some buttons that perform operations on the tree.
    """

    def compose(self) -> ComposeResult:
        yield MyTree("Test")
        yield Button('Refresh leaf', id='refresh_leaf')
        yield Button('Refresh branch', id='refresh_branch')

    def on_mount(self) -> None:
        tree = self.query_one(Tree)
        tree.root.expand()
        self.branch = tree.root.add('Branch', expand=True)
        self.leaf = self.branch.add_leaf('Leaf')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'refresh_leaf':
            node = self.leaf
        else:
            node = self.branch
        tree = self.query_one(Tree)
        tree.test_counter += 1
        tree.refresh_line(node.line)


async def test_refresh_leaf() -> None:
    """A leaf node re-renders when refresh_line is invoked.

    Regression test for https://github.com/Textualize/textual/issues/3637
    """
    async with TreeApp().run_test() as pilot:
        tree = pilot.app.query_one(Tree)

        await pilot.click('#refresh_leaf')
        assert '1 Leaf' in tree.render_history
        assert '1 Branch' not in tree.render_history

        await pilot.click('#refresh_leaf')
        assert '2 Leaf' in tree.render_history
        assert '2 Branch' not in tree.render_history


async def test_refresh_branch() -> None:
    """A branch node re-renders when refresh_line is invoked.

    Regression test for https://github.com/Textualize/textual/issues/3637
    """
    async with TreeApp().run_test() as pilot:
        tree = pilot.app.query_one(Tree)

        await pilot.click('#refresh_branch')
        assert '1 Branch' in tree.render_history
        assert '1 Leaf' not in tree.render_history

        await pilot.click('#refresh_branch')
        assert '2 Branch' in tree.render_history
        assert '2 Leaf' not in tree.render_history
