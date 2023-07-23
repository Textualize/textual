from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree


class DirectoryTreeReloadApp(App[None]):
    """DirectoryTree reloading test app."""

    def __init__(self, path):
        super().__init__()
        self._tmp_path = path

    def compose(self) -> ComposeResult:
        yield DirectoryTree(self._tmp_path)


async def test_directory_tree_reload_node(tmp_path) -> None:
    """Reloading a node of a directory tree should display newly created file inside the directory."""

    RELOADED_DIRECTORY = "parentdir"
    NOT_RELOADED_DIRECTORY = "otherdir"
    FILE1_NAME = "log.txt"
    FILE2_NAME = "hello.txt"
    NOT_RELOADED_FILE3_NAME = "demo.txt"
    NOT_RELOADED_FILE4_NAME = "unseen.txt"

    reloaded_dir = tmp_path / RELOADED_DIRECTORY
    reloaded_dir.mkdir()
    non_reloaded_dir = tmp_path / NOT_RELOADED_DIRECTORY
    non_reloaded_dir.mkdir()
    file1 = reloaded_dir / FILE1_NAME
    file1.touch()
    file3 = non_reloaded_dir / NOT_RELOADED_FILE3_NAME
    file3.touch()
    async with DirectoryTreeReloadApp(tmp_path).run_test() as pilot:
        await pilot.pause()
        tree = pilot.app.query_one(DirectoryTree)
        assert len(tree.root.children) == 2
        node = tree.root.children[1]
        assert node.label == Text(RELOADED_DIRECTORY)
        node.expand()
        await pilot.pause()
        assert len(node.children) == 1
        assert node.children[0].label == Text(FILE1_NAME)
        unaffected_node = tree.root.children[0]
        unaffected_node.expand()
        await pilot.pause()
        assert len(unaffected_node.children) == 1
        assert unaffected_node.children[0].label == Text(NOT_RELOADED_FILE3_NAME)

        file2 = reloaded_dir / FILE2_NAME
        file2.touch()
        file4 = non_reloaded_dir / NOT_RELOADED_FILE4_NAME
        file4.touch()
        tree.reload_node(node)

        await pilot.pause()
        assert len(tree.root.children) == 2
        node = tree.root.children[1]
        assert node.label == Text(RELOADED_DIRECTORY)
        node.collapse()
        node.expand()
        assert len(node.children) == 2
        assert [child.label for child in node.children] == [
            Text(filename) for filename in sorted({FILE1_NAME, FILE2_NAME})
        ]
        unaffected_node.collapse()
        unaffected_node.expand()
        assert len(unaffected_node.children) == 1
        assert unaffected_node.children[0].label == Text(NOT_RELOADED_FILE3_NAME)
