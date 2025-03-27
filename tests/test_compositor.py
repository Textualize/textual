from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static


async def test_compositor_scroll_placements():
    """Regression test for https://github.com/Textualize/textual/issues/5249
    The Static should remain visible.
    """

    class ScrollApp(App):
        CSS = """
        Screen {
            overflow: scroll;
        }
        Container {
            width: 200vw;
        }
        #hello {
            width: 20;
            height: 10;
            offset: 50 10;
            background: blue;
            color: white;
        }
        """

        def compose(self) -> ComposeResult:
            with Container():
                yield Static("Hello", id="hello")

        def on_mount(self) -> None:
            self.screen.scroll_to(20, 0, animate=False)

    app = ScrollApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        static = app.query_one("#hello")
        widgets = app.screen._compositor.visible_widgets
        # The static wasn't scrolled out of view, and should be visible
        # This wasn't the case <= v0.86.1
        assert static in widgets
