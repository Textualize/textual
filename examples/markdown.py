from pathlib import Path

from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Footer, MarkdownViewer


class MarkdownApp(App):
    BINDINGS = [
        ("t", "toggle_table_of_contents", "TOC"),
        ("b", "back", "Back"),
        ("f", "forward", "Forward"),
    ]

    path = var(Path(__file__).parent / "demo.md")

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_one(MarkdownViewer)

    def compose(self) -> ComposeResult:
        yield Footer()
        yield MarkdownViewer()

    async def on_mount(self) -> None:
        self.markdown_viewer.focus()
        if not await self.markdown_viewer.go(self.path):
            self.exit(message=f"Unable to load {self.path!r}")

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = (
            not self.markdown_viewer.show_table_of_contents
        )

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()


if __name__ == "__main__":
    app = MarkdownApp()
    app.run()
