from textual import containers, widgets
from textual.app import App, ComposeResult
from textual.layouts.grid import GridLayout


async def test_grid_size():
    """Test the `grid_size` property on GridLayout."""

    class GridApp(App):
        CSS = """
        Grid {
            grid-size: 3;
            grid-columns: auto;
            height: auto;
            Label {
                padding: 2 4;
                border: blue;
            }
        }
        """

        def compose(self) -> ComposeResult:
            with containers.VerticalScroll():
                with containers.Grid():
                    for _ in range(7):
                        yield widgets.Label("Hello, World!")

    app = GridApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await app.wait_for_refresh()
        grid_layout = app.query_one(containers.Grid).layout
        assert isinstance(grid_layout, GridLayout)
        assert grid_layout.grid_size == (3, 3)
