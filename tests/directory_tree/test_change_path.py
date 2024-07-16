from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree


class DirectoryTreeApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")


async def test_change_directory_tree_path(tmpdir: Path) -> None:
    """The DirectoryTree should react to the path changing."""

    async with DirectoryTreeApp().run_test() as pilot:
        assert pilot.app.query_one(DirectoryTree).root.data.path == Path(".")
        pilot.app.query_one(DirectoryTree).path = tmpdir
        await pilot.pause()
        assert pilot.app.query_one(DirectoryTree).root.data.path == tmpdir
