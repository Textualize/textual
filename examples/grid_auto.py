from textual.app import App
from textual import events
from textual.widgets import Placeholder


class GridTest(App):
    async def on_mount(self, event: events.Mount) -> None:
        """Create a grid with auto-arranging cells."""

        grid = await self.screen.dock_grid()

        grid.add_column("col", fraction=1, max_size=20)
        grid.add_row("row", fraction=1, max_size=10)
        grid.set_repeat(True, True)
        grid.add_areas(center="col-2-start|col-4-end,row-2-start|row-3-end")
        grid.set_align("stretch", "center")

        placeholders = [Placeholder() for _ in range(20)]
        grid.place(*placeholders, center=Placeholder())


GridTest.run(title="Grid Test", log_path="textual.log")
