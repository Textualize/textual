from textual.app import App, ComposeResult
from textual.widgets import Header, Static

TEXT = """\
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.

Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

"""


class DockLayoutExample(App):
    CSS_PATH = "dock_layout3_sidebar_header.tcss"

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Static("Sidebar1", id="sidebar")
        yield Static(TEXT * 10, id="body")


if __name__ == "__main__":
    app = DockLayoutExample()
    app.run()
