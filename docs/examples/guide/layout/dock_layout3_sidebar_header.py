from textual.app import App, ComposeResult
from textual.widgets import Static, Header

TEXT = """\
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.

Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

"""


class DockLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Static("Sidebar1", id="sidebar")
        yield Static(TEXT * 10, id="body")


app = DockLayoutExample(css_path="dock_layout3_sidebar_header.css")
if __name__ == "__main__":
    app.run()
