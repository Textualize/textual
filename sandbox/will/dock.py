from textual.app import App, ComposeResult
from textual.widgets import Static


class DockApp(App):
    def compose(self) -> ComposeResult:

        self.screen.styles.layers = "base sidebar"

        header = Static("Header", id="header")
        header.styles.dock = "top"
        header.styles.height = "3"

        header.styles.background = "blue"
        header.styles.color = "white"
        header.styles.margin = 0
        header.styles.align_horizontal = "center"

        # header.styles.layer = "base"

        header.styles.box_sizing = "border-box"

        yield header

        footer = Static("Footer")
        footer.styles.dock = "bottom"
        footer.styles.height = 1
        footer.styles.background = "green"
        footer.styles.color = "white"

        yield footer

        sidebar = Static("Sidebar", id="sidebar")
        sidebar.styles.dock = "right"
        sidebar.styles.width = 20
        sidebar.styles.height = "100%"
        sidebar.styles.background = "magenta"
        # sidebar.styles.layer = "sidebar"

        yield sidebar

        for n, color in zip(range(5), ["red", "green", "blue", "yellow", "magenta"]):
            thing = Static(f"Thing {n}", id=f"#thing{n}")
            thing.styles.border = ("heavy", "rgba(0,0,0,0.2)")
            thing.styles.background = f"{color} 20%"
            thing.styles.height = 15
            yield thing


app = DockApp()
if __name__ == "__main__":
    app.run()
