from rich.markdown import Markdown

from textual.app import App
from textual.widgets import Header, Footer, Placeholder, ScrollView


class MyApp(App):
    """An example of a very simple Textual App"""

    stylesheet = """

    App > View {
        layout: dock
    }

    #body {
        padding: 1
    }

    #sidebar {
        edge left
        size: 40
    }

    """

    async def on_load(self) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Create and dock the widgets."""

        body = ScrollView()
        await self.screen.mount(
            Header(),
            Footer(),
            body=body,
            sidebar=Placeholder(),
        )

        async def get_markdown(filename: str) -> None:
            with open(filename, "rt") as fh:
                readme = Markdown(fh.read(), hyperlinks=True)
            await body.update(readme)

        await self.call_later(get_markdown, "richreadme.md")


MyApp.run(title="Simple App", log_path="textual.log")
