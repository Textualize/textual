from pathlib import Path

import pytest
from rich.text import Text

import textual.widgets._markdown as MD
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Markdown, MarkdownViewer, Tree

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
        yield MarkdownViewer(open_links=False)

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
    def __init__(self, markdown_string: str) -> None:
        self.markdown_string = markdown_string
        super().__init__()

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self.markdown_string, open_links=False)

    async def on_mount(self) -> None:
        self.query_one(MarkdownViewer).show_table_of_contents = False


@pytest.mark.parametrize("link", [0, 1])
async def test_markdown_string_viewer_anchor_link(link: int) -> None:
    """Test https://github.com/Textualize/textual/issues/3094

    Also https://github.com/Textualize/textual/pull/3244#issuecomment-1710278718."""
    async with MarkdownStringViewerApp(
        TEST_MARKDOWN.replace("{{file}}", "")
    ).run_test() as pilot:
        # There's not really anything to test *for* here, but the lack of an
        # exception is the win (before the fix this is testing it would have
        # been FileNotFoundError).
        await pilot.click(Markdown, Offset(2, link))


@pytest.mark.parametrize("text", ["Hey [[/test]]", "[i]Hey there[/i]"])
async def test_headings_that_look_like_they_contain_markup(text: str) -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3689.

    Things that look like markup are escaped in markdown headings in the table of contents.
    """

    document = f"# {text}"
    async with MarkdownStringViewerApp(document).run_test() as pilot:
        assert pilot.app.query_one(MD.MarkdownH1)._text == Text(text)
        toc_tree = pilot.app.query_one(MD.MarkdownTableOfContents).query_one(Tree)
        # The toc label looks like "I {text}" but the I is styled so we drop it.
        toc_label = toc_tree.root.children[0].label
        _, text_label = toc_label.divide([2])
        assert text_label == Text(text)
