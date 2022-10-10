from rich.markdown import Markdown

from textual.app import App
from textual.layouts.grid import GridLayout
from textual.widgets import ScrollView, Tab, TabBar


# The repos' directory's name
REPOS = ["rich", "textual"]
# A directory containing the repos above
REPOS_DIRECTORY = "/home/<user>/repositories/"


class MyTabBar(TabBar):
    def init_grid(self, grid: GridLayout) -> None:
        max_row = len(self._tabs)
        grid.add_column("col")
        grid.add_row("bar", repeat=max_row, size=10)


class ReadMe(App):
    """Show the README of the given repositories."""

    async def on_mount(self) -> None:
        tabs = []

        # Create tabs with their related Renderable
        for repo_name in REPOS:
            with open(f"{REPOS_DIRECTORY}{repo_name}/README.md", "r") as f:
                content = Markdown(f.read())

            tabs.append(Tab(content, name=repo_name))

        # Create the main view, used by TabBar to change content
        main_view = ScrollView()

        # Different ways to implement the TabBar
        if False:
            # On top (default) :
            tab_bar = TabBar(tabs, main_view)
            await self.view.dock(tab_bar, edge="top", size=20)
        else:
            # On left (by overriding init_grid):
            tab_bar = MyTabBar(tabs, main_view)
            await self.view.dock(tab_bar, edge="left", size=20)

        await self.view.dock(main_view)


ReadMe.run(log="textual.log")
