from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.screen import ModalScreen
from textual.widgets import Footer, Label


async def test_footer_highlight_when_pushing_modal():
    """Regression test for https://github.com/Textualize/textual/issues/2606"""

    class MyModalScreen(ModalScreen):
        def compose(self) -> ComposeResult:
            yield Label("apple")

    class MyApp(App[None]):
        BINDINGS = [("a", "p", "push")]

        def compose(self) -> ComposeResult:
            yield Footer()

        def action_p(self):
            self.push_screen(MyModalScreen())

    app = MyApp()
    async with app.run_test(size=(80, 2)) as pilot:
        await pilot.hover(None, Offset(0, 1))
        await pilot.click(None, Offset(0, 1))
        assert isinstance(app.screen, MyModalScreen)
        assert app.screen_stack[0].query_one(Footer).highlight_key is None
