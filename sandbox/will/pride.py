from textual.app import App, ComposeResult
from textual.widgets import Static


class PrideApp(App):
    """Displays a pride flag."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    def compose(self) -> ComposeResult:
        for color in self.COLORS:
            stripe = Static()
            stripe.styles.height = "1fr"
            stripe.styles.background = color
            yield stripe


if __name__ == "__main__":
    app = PrideApp()

    from rich import print

    async def run_app():
        async with app.run_managed() as pilot:
            await pilot.pause(5)

    import asyncio

    asyncio.run(run_app())
