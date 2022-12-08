from textual.app import App, ComposeResult
from textual.widgets import Static

TEXT = """\
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.

Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

"""


class DockLayoutExample(App):
    CSS_PATH = "dock_layout2_sidebar.css"

    def compose(self) -> ComposeResult:
        yield Static("Sidebar2", id="another-sidebar")
        yield Static("Sidebar1", id="sidebar")
        yield Static(TEXT * 10, id="body")


app = DockLayoutExample()
if __name__ == "__main__":
    app.run()
