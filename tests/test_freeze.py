import pytest

from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, Label


class MyScreen(Screen):
    def compose(self):
        yield Header()
        yield Input()
        yield Footer()


class MyApp(App):
    def on_mount(self):
        self.install_screen(MyScreen(), "myscreen")
        self.push_screen("myscreen")


async def test_freeze():
    """Regression test for https://github.com/Textualize/textual/issues/1608"""
    app = MyApp()
    with pytest.raises(Exception):
        async with app.run_test():
            raise Exception("never raised")


async def test_button_freeze():
    class MyModal(ModalScreen[str | None]):
        BINDINGS = [("escape", "cancel", "Cancel")]

        def __init__(self, s: str):
            self._s = s
            super().__init__()

        def compose(self) -> ComposeResult:
            with ScrollableContainer():
                yield Label("My Screen")
                yield Button("Save", id="save", variant="success")
            yield Footer()

        @on(Button.Pressed, "#save")
        def handle_save(self) -> None:
            self.dismiss("Yes" if (self._s == "Hello!") else None)

        def action_cancel(self) -> None:
            self.dismiss(None)

    class MyApp(App):
        BINDINGS = [("m", "modal", "Show modal")]

        def compose(self) -> ComposeResult:
            yield Footer()

        def action_modal(self) -> None:
            s = "Hello!"
            self.push_screen(MyModal(s))

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("tab", "return")
