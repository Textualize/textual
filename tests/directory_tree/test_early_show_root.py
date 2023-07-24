from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree


class DirectoryTreeApp(App[None]):
    def compose(self) -> ComposeResult:
        tree = DirectoryTree(".")
        tree.show_root = True
        yield tree


async def test_managed_to_set_show_root_before_mounted() -> None:
    """https://github.com/Textualize/textual/issues/2363"""
    async with DirectoryTreeApp().run_test() as pilot:
        assert isinstance(pilot.app.query_one(DirectoryTree), DirectoryTree)
        assert pilot.app.query_one(DirectoryTree).show_root is True
