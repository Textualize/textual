from textual.app import App
from textual.widgets import Placeholder


class BasicApp(App):
    """Demonstrates smooth animation. Press 'b' to see it in action."""

    css = """

    App > View {
        layout: dock
    }

    #widget1 {
        edge: top
    }

    #widget2 {


    }

    """

    async def on_mount(self) -> None:
        """Build layout here."""

        await self.view.mount(widget1=Placeholder(), widget2=Placeholder())


SmoothApp.run(log="textual.log")
