from pathlib import Path

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Markdown, MarkdownViewer

class MarkdownViewerApp(App[None]):

    def compose(self) -> ComposeResult:
        yield MarkdownViewer()

    async def on_mount(self) -> None:
        self.query_one(MarkdownViewer).show_table_of_contents = False
        await self.query_one(MarkdownViewer).go(
            Path(__file__).with_suffix(".md")
        )


async def test_markdown_viewer_anchor_link() -> None:
    """Test https://github.com/Textualize/textual/issues/3094"""
    async with MarkdownViewerApp().run_test() as pilot:
        # There's not really anything to test *for* here, but the lack of an
        # exception is the win (before the fix this is testing it would have
        # been FileNotFoundError).
        await pilot.click(Markdown, Offset(2, 1))
