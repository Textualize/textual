import pytest

from textual.app import App
from textual.screen import Screen
from textual.widgets import Footer, Header, Input


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
