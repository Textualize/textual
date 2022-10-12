from rich.markdown import Markdown

from textual.app import App
from textual.layouts.grid import GridLayout
from textual.widgets import ScrollView, Tab, TabBar


# The repos' directory's name
REPOS = ["rich", "textual"]
# A directory containing the repos above
REPOS_DIRECTORY = "/home/<user>/repositories/"


class MyTab(Tab):
    @property
    def color(self) -> str:
        if self.hover:
            return "on blue"
        elif self.selected:
            return "on yellow"
        else:
            return ""


class MyTabBar(TabBar):
    SIZE = 3

    def init_grid(self, grid: GridLayout) -> None:
        max_row = len(self._tabs)
        grid.add_column("col")
        grid.add_row("bar", repeat=max_row, size=self.SIZE)


class ReadMe(App):
    """Show the README of the given repositories."""

    async def on_mount(self) -> None:
        tabs = []

        # Create tabs with their related Renderable
        for repo_name in REPOS:
            with open(f"{REPOS_DIRECTORY}{repo_name}/README.md", "r") as f:
                content = Markdown(f.read())

            # Create duplicated tabs to show possibilities about colors
            tabs.append(Tab(content, name=f"{repo_name} RED"))
            tabs.append(MyTab(content, name=f"{repo_name} BLUE"))

        # Create the main view, used by TabBar to change content
        main_view = ScrollView()

        # Different ways to implement the TabBar
        if False:
            # On top (default) :
            tab_bar = TabBar(tabs, main_view)
            await self.view.dock(tab_bar, edge="top", size=tab_bar.SIZE)
        else:
            # On left (by overriding init_grid):
            tab_bar = MyTabBar(tabs, main_view)
            await self.view.dock(tab_bar, edge="left", size=tab_bar.SIZE)

        await self.view.dock(main_view)


ReadMe.run(log="textual.log")
