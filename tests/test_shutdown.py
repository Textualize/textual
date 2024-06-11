from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Footer, Tree


class TreeApp(App[None]):
    def compose(self):
        yield Horizontal(Tree("Dune"))
        yield Footer()


async def test_shutdown():
    # regression test for https://github.com/Textualize/textual/issues/4634
    # Testing that an app with the footer doesn't deadlock
    app = TreeApp()
    print("Check for deadlock in test_shutdown.py")
    async with app.run_test():
        pass
