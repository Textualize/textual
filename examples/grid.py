from textual.app import App
from textual import events
from textual.widgets import Placeholder


class GridTest(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q,ctrl+c", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:

        grid = await self.view.dock_grid(edge="left", size=70, name="left")
        left = self.view["left"]

        grid.add_column(fraction=1, name="left", min_size=20)
        grid.add_column(size=30, name="center")
        grid.add_column(fraction=1, name="right")

        grid.add_row(fraction=1, name="top", min_size=2)
        grid.add_row(fraction=2, name="middle")
        grid.add_row(fraction=1, name="bottom")

        grid.add_areas(
            area1="left,top",
            area2="center,middle",
            area3="left-start|right-end,bottom",
            area4="right,top-start|middle-end",
        )

        def make_placeholder(name: str) -> Placeholder:
            p = Placeholder(name=name)
            p.layout_offset_x = 10
            p.layout_offset_y = 0
            return p

        grid.place(
            area1=make_placeholder(name="area1"),
            area2=make_placeholder(name="area2"),
            area3=make_placeholder(name="area3"),
            area4=make_placeholder(name="area4"),
        )


GridTest.run(title="Grid Test")
