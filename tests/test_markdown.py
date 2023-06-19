"""Unit tests for the Markdown widget."""

from __future__ import annotations

from typing import Iterator

import pytest

import textual.widgets._markdown as MD
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Markdown


class MarkdownApp(App[None]):
    def __init__(self, markdown: str) -> None:
        super().__init__()
        self._markdown = markdown

    def compose(self) -> ComposeResult:
        yield Markdown(self._markdown)


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
        ("- One\n-Two", [MD.MarkdownBulletList]),
        ("1. One\n2. Two", [MD.MarkdownOrderedList]),
        ("```\n1\n```", [MD.MarkdownFence]),
        ("```python\n1\n```", [MD.MarkdownFence]),
        ("""| One | Two |\n| :- | :- |\n| 1 | 2 |""", [MD.MarkdownTable]),
    ],
)
async def test_markdown_nodes(
    document: str, expected_nodes: list[Widget | list[Widget]]
) -> None:
    """A Markdown document should parse into the expected Textual node list."""

    def markdown_nodes(root: Markdown | MD.MarkdownBlock) -> Iterator[MD.MarkdownBlock]:
        for node in root.children:
            if isinstance(node, MD.MarkdownBlock):
                yield node
                yield from markdown_nodes(node)

    async with MarkdownApp(document).run_test() as pilot:
        assert [
            node.__class__ for node in markdown_nodes(pilot.app.query_one(Markdown))
        ] == expected_nodes
