from pathlib import Path

import pytest

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Markdown, MarkdownViewer

TEST_MARKDOWN = """\
* [First]({{file}}#first)
* [Second](#second)

# First

The first.

# Second

The second.
"""


class MarkdownFileViewerApp(App[None]):
    def __init__(self, markdown_file: Path) -> None:
        super().__init__()
        self.markdown_file = markdown_file
        markdown_file.write_text(TEST_MARKDOWN.replace("{{file}}", markdown_file.name))

    def compose(self) -> ComposeResult:
        yield MarkdownViewer()

    async def on_mount(self) -> None:
        self.query_one(MarkdownViewer).show_table_of_contents = False
        await self.query_one(MarkdownViewer).go(self.markdown_file)


@pytest.mark.parametrize("link", [0, 1])
async def test_markdown_file_viewer_anchor_link(tmp_path, link: int) -> None:
    """Test https://github.com/Textualize/textual/issues/3094"""
    async with MarkdownFileViewerApp(Path(tmp_path) / "test.md").run_test() as pilot:
        # There's not really anything to test *for* here, but the lack of an
        # exception is the win (before the fix this is testing it would have
        # been FileNotFoundError).
        await pilot.click(Markdown, Offset(2, link))


class MarkdownStringViewerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield MarkdownViewer(TEST_MARKDOWN.replace("{{file}}", ""))

    async def on_mount(self) -> None:
        self.query_one(MarkdownViewer).show_table_of_contents = False


@pytest.mark.parametrize("link", [0, 1])
async def test_markdown_string_viewer_anchor_link(link: int) -> None:
    """Test https://github.com/Textualize/textual/issues/3094

    Also https://github.com/Textualize/textual/pull/3244#issuecomment-1710278718."""
    async with MarkdownStringViewerApp().run_test() as pilot:
        # There's not really anything to test *for* here, but the lack of an
        # exception is the win (before the fix this is testing it would have
        # been FileNotFoundError).
        await pilot.click(Markdown, Offset(2, link))
