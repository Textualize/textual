from textual.app import App
from textual.widgets import Placeholder


class BasicApp(App):
    """A basic app demonstrating CSS"""

    css = """

    App > DockView {
        layout: dock;
        docks: sidebar=left widgets=top;
    }

    #sidebar {
        dock-group: sidebar;
        width: 40;
    }

    #widget1 {
        text: on blue;
        dock-group: widgets;
        height: 1fr;
    }

    #widget2 {
        text: on red;
        dock-group: widgets;
        height: 1fr;
    }

    """

    async def on_mount(self) -> None:
        """Build layout here."""
        await self.view.mount(
            sidebar=Placeholder(), widget1=Placeholder(), widget2=Placeholder()
        )


BasicApp.run(log="textual.log")
