from __future__ import annotations

import sys

from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Footer

from ._markdown import MarkdownBrowser


class BrowserApp(App):
    BINDINGS = [
        ("t", "toggle_toc", "TOC"),
        ("b", "back", "Back"),
        ("f", "forward", "Forward"),
    ]

    path = var("")

    def compose(self) -> ComposeResult:
        yield Footer()
        yield MarkdownBrowser()

    @property
    def browser(self) -> MarkdownBrowser:
        return self.query_one(MarkdownBrowser)

    def on_load(self) -> None:
        try:
            path = sys.argv[1]
        except IndexError:
            self.exit(message="Usage: python -m textual_markdown PATH")
        else:
            self.path = path

    async def on_mount(self) -> None:
        self.browser.focus()
        if not await self.browser.go(self.path):
            self.exit(message=f"Unable to load {self.path!r}")

    async def load(self, path: str) -> None:
        await self.browser.go(path)

    def action_toggle_toc(self) -> None:
        self.browser.show_toc = not self.browser.show_toc

    async def action_back(self) -> None:
        await self.browser.back()

    async def action_forward(self) -> None:
        await self.browser.forward()


if __name__ == "__main__":
    app = BrowserApp()
    app.run()
