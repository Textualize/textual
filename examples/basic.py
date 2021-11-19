from textual.app import App
from textual.widgets import Placeholder


class BasicApp(App):
    """A basic app demonstrating CSS"""

    css = """

    App > DockView {
        layout: dock;
        docks: sidebar=left | widgets=top;
    }

    #sidebar {
        dock-group: sidebar;
    }

    #widget1 {
        text-background: blue;
        dock-group: widgets;
    }

    #widget2 {
        text: on red;
        dock-group: widgets;
    }

    """

    async def on_mount(self) -> None:
        """Build layout here."""
        self.log("MOUNT")
        await self.view.mount(
            sidebar=Placeholder(), widget1=Placeholder(), widget2=Placeholder()
        )
        self.log("MOUNTED CHILDREN", self.view.children)


BasicApp.run(log="textual.log")
