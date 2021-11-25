from textual.app import App
from textual.widget import Widget


class BasicApp(App):
    """A basic app demonstrating CSS"""

    css = """

    App > DockView {
        layout: dock;
        docks: side=left/1 header=top footer=bottom;
        layers: base panels;
    }

    #sidebar {
        text: bold #09312e on #3CAEA3;
        dock-group: side;
        width: 30;
        height: 1fr;
        layer: panels;
        border-right: vkey #09312e;
        display: block;
        offset-x: -15
    }

    #sidebar.-active {
        display: block;
    }

    #header {
        text: on #173f5f;
        dock-group: header;
        height: 3;
        border: hkey white;
    }

    #footer {
        dock-group: header;

        /* border-top: hkey #0f2b41; */
        text: #3a3009 on #f6d55c;
        /*padding: 2;*/
        border: heavy red;
         margin: 2;

    }

    #content {
        dock-group: header;
        text: on #20639B;
    }


    """

    async def on_load(self) -> None:
        await self.bind("t", "toggle('#sidebar', '-active')")

    async def on_mount(self) -> None:
        """Build layout here."""

        await self.view.mount(
            header=Widget(),
            content=Widget(),
            footer=Widget(),
            sidebar=Widget(),
        )


BasicApp.run(log="textual.log")
