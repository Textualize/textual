from textual.app import App
from textual.widgets import Label


class LinkHoverBackgroundApp(App):
    def compose(self):
        yield Label(
            "Visit the [link=https://textualize.io]Textualize[/link] website.",
            id="lbl1",  # (1)!
        )
        yield Label(
            "Click [@click=app.bell]here[/] for the bell sound.",
            id="lbl2",  # (2)!
        )
        yield Label(
            "You can also click [@click=app.bell]here[/] for the bell sound.",
            id="lbl3",  # (3)!
        )
        yield Label(
            "[@click=app.quit]Exit this application.[/]",
            id="lbl4",  # (4)!
        )


app = LinkHoverBackgroundApp(css_path="link_hover_background.css")
