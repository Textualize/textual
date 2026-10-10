from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import TextArea
from textual.geometry import Region

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

async def test_modal_textarea():
    app = Demo()
    async with app.run_test() as pilot:
        await pilot.pause()

class CustomTextArea(TextArea):
    COMPONENT_CLASSES = set()
    _inherit_component_classes = False

class CustomCredsModal(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        yield CustomTextArea("", id="ta", language=None, show_line_numbers=False)

class CustomDemo(App):
    def on_mount(self) -> None:
        self.push_screen(CustomCredsModal())

async def test_custom_textarea_no_component_classes():
    app = CustomDemo()
    async with app.run_test() as pilot:
        await pilot.pause()
        text_area = app.screen.query_one(CustomTextArea)
        text_area.render_lines(Region(0, 0, 80, 10))
