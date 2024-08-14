from __future__ import annotations

from pathlib import Path
from sys import argv

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import var
from textual.widgets import Footer, MarkdownViewer


class MarkdownApp(App):
    """A simple Markdown viewer application."""

    BINDINGS = [
        Binding(
            "t",
            "toggle_table_of_contents",
            "TOC",
            tooltip="Toggle the Table of Contents Panel",
        ),
        Binding("b", "back", "Back", tooltip="Navigate back"),
        Binding("f", "forward", "Forward", tooltip="Navigate forward"),
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
        """Go to the first path when the app starts."""
        try:
            await self.markdown_viewer.go(self.path)
        except FileNotFoundError:
            self.exit(message=f"Unable to load {self.path!r}")

    def on_markdown_viewer_navigator_updated(self) -> None:
        """Refresh bindings for forward / back when the document changes."""
        self.refresh_bindings()

    def action_toggle_table_of_contents(self) -> None:
        """Toggles display of the table of contents."""
        self.markdown_viewer.show_table_of_contents = (
            not self.markdown_viewer.show_table_of_contents
        )

    async def action_back(self) -> None:
        """Navigate backwards."""
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        """Navigate forwards."""
        await self.markdown_viewer.forward()

    def check_action(self, action: str, _) -> bool | None:
        """Check if certain actions can be performed."""
        if action == "forward" and self.markdown_viewer.navigator.end:
            # Disable footer link if we can't go forward
            return None
        if action == "back" and self.markdown_viewer.navigator.start:
            # Disable footer link if we can't go backward
            return None
        # All other keys display as normal
        return True


if __name__ == "__main__":
    app = MarkdownApp()
    if len(argv) > 1 and Path(argv[1]).exists():
        app.path = Path(argv[1])
    app.run()
