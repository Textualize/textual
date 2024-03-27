"""Unit tests for the Markdown widget."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from markdown_it.token import Token
from rich.style import Style
from rich.text import Span

import textual.widgets._markdown as MD
from textual import on
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Markdown
from textual.widgets.markdown import MarkdownBlock


class UnhandledToken(MarkdownBlock):
    def __init__(self, markdown: Markdown, token: Token) -> None:
        super().__init__(markdown)
        self._token = token

    def __repr___(self) -> str:
        return self._token.type


class FussyMarkdown(Markdown):
    def unhandled_token(self, token: Token) -> MarkdownBlock | None:
        return UnhandledToken(self, token)


class MarkdownApp(App[None]):
    def __init__(self, markdown: str) -> None:
        super().__init__()
        self._markdown = markdown

    def compose(self) -> ComposeResult:
        yield FussyMarkdown(self._markdown)


@pytest.mark.parametrize(
    ["document", "expected_nodes"],
    [
        # Basic markup.
        ("", []),
        ("# Hello", [MD.MarkdownH1]),
        ("## Hello", [MD.MarkdownH2]),
        ("### Hello", [MD.MarkdownH3]),
        ("#### Hello", [MD.MarkdownH4]),
        ("##### Hello", [MD.MarkdownH5]),
        ("###### Hello", [MD.MarkdownH6]),
        ("---", [MD.MarkdownHorizontalRule]),
        ("Hello", [MD.MarkdownParagraph]),
        ("Hello\nWorld", [MD.MarkdownParagraph]),
        ("> Hello", [MD.MarkdownBlockQuote, MD.MarkdownParagraph]),
        ("- One\n-Two", [MD.MarkdownBulletList, MD.MarkdownParagraph]),
        (
            "1. One\n2. Two",
            [MD.MarkdownOrderedList, MD.MarkdownParagraph, MD.MarkdownParagraph],
        ),
        ("    1", [MD.MarkdownFence]),
        ("```\n1\n```", [MD.MarkdownFence]),
        ("```python\n1\n```", [MD.MarkdownFence]),
        ("""| One | Two |\n| :- | :- |\n| 1 | 2 |""", [MD.MarkdownTable]),
        # Test for https://github.com/Textualize/textual/issues/2676
        (
            "- One\n```\nTwo\n```\n- Three\n",
            [
                MD.MarkdownBulletList,
                MD.MarkdownParagraph,
                MD.MarkdownFence,
                MD.MarkdownBulletList,
                MD.MarkdownParagraph,
            ],
        ),
    ],
)
async def test_markdown_nodes(
    document: str, expected_nodes: list[Widget | list[Widget]]
) -> None:
    """A Markdown document should parse into the expected Textual node list."""

    def markdown_nodes(root: Widget) -> Iterator[MarkdownBlock]:
        for node in root.children:
            if isinstance(node, MarkdownBlock):
                yield node
            yield from markdown_nodes(node)

    async with MarkdownApp(document).run_test() as pilot:
        assert [
            node.__class__ for node in markdown_nodes(pilot.app.query_one(Markdown))
        ] == expected_nodes


async def test_softbreak_split_links_rendered_correctly() -> None:
    """Test for https://github.com/Textualize/textual/issues/2805"""

    document = """\
My site [has
this
URL](https://example.com)\
"""
    async with MarkdownApp(document).run_test() as pilot:
        markdown = pilot.app.query_one(Markdown)
        paragraph = markdown.children[0]
        assert isinstance(paragraph, MD.MarkdownParagraph)
        assert paragraph._text.plain == "My site has this URL"
        expected_spans = [
            Span(8, 11, Style(meta={"@click": "link('https://example.com')"})),
            Span(11, 12, Style(meta={"@click": "link('https://example.com')"})),
            Span(12, 16, Style(meta={"@click": "link('https://example.com')"})),
            Span(16, 17, Style(meta={"@click": "link('https://example.com')"})),
            Span(17, 20, Style(meta={"@click": "link('https://example.com')"})),
        ]

    assert paragraph._text.spans == expected_spans


async def test_load_non_existing_file() -> None:
    """Loading a file that doesn't exist should result in the obvious error."""
    async with MarkdownApp("").run_test() as pilot:
        with pytest.raises(FileNotFoundError):
            await pilot.app.query_one(Markdown).load(
                Path("---this-does-not-exist---.it.is.not.a.md")
            )


@pytest.mark.parametrize(
    ("anchor", "found"),
    [
        ("hello-world", False),
        ("hello-there", True),
    ],
)
async def test_goto_anchor(anchor: str, found: bool) -> None:
    """Going to anchors should return a boolean: whether the anchor was found."""
    document = "# Hello There\n\nGeneral.\n"
    async with MarkdownApp(document).run_test() as pilot:
        markdown = pilot.app.query_one(Markdown)
        assert markdown.goto_anchor(anchor) is found


async def test_update_of_document_posts_table_of_content_update_message() -> None:
    """Updating the document should post a TableOfContentsUpdated message."""

    messages: list[str] = []

    class TableOfContentApp(App[None]):

        def compose(self) -> ComposeResult:
            yield Markdown("# One\n\n#Two\n")

        @on(Markdown.TableOfContentsUpdated)
        def log_table_of_content_update(
            self, event: Markdown.TableOfContentsUpdated
        ) -> None:
            nonlocal messages
            messages.append(event.__class__.__name__)

    async with TableOfContentApp().run_test() as pilot:
        assert messages == ["TableOfContentsUpdated"]
        pilot.app.query_one(Markdown).update("")
        await pilot.pause()
        assert messages == ["TableOfContentsUpdated", "TableOfContentsUpdated"]
