from pathlib import Path
from sys import argv

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
        try:
            await self.markdown_viewer.go(self.path)
        except FileNotFoundError:
            self.exit(message=f"Unable to load {self.path!r}")

    def on_markdown_viewer_navigator_updated(self) -> None:
        self.refresh_bindings()

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = (
            not self.markdown_viewer.show_table_of_contents
        )

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "forward" and self.markdown_viewer.navigator.end:
            return None
        if action == "back" and self.markdown_viewer.navigator.start:
            return None
        return True


if __name__ == "__main__":
    app = MarkdownApp()
    if len(argv) > 1 and Path(argv[1]).exists():
        app.path = Path(argv[1])
    app.run()
