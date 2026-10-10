import pytest
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import TextArea


class CredsModal(ModalScreen[None]):
    CSS = """
    #box {
        width: 80;
        height: 20;
        border: heavy white;
    }
    #ta {
        height: 10;
        border: solid white;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="box"):
            yield TextArea("", id="ta", language=None, show_line_numbers=False)


class Demo(App):
    def on_mount(self) -> None:
        self.push_screen(CredsModal())


@pytest.mark.asyncio
async def test_issue_6528_modal_textarea_no_crash():
    app = Demo()
    async with app.run_test() as pilot:
        # Pushing a ModalScreen and rendering the TextArea inside should not crash
        await pilot.pause()
        ta = app.screen.query_one(TextArea)
        assert ta is not None
        # Call render_lines explicitly to ensure apply_css is executed
        from textual.geometry import Region
        ta.render_lines(Region(0, 0, 80, 10))
