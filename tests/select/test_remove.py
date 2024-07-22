from textual.app import App, ComposeResult
from textual.widgets import Header, Select

LINES = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.""".splitlines()


async def test_select_remove():
    # Regression test for https://github.com/Textualize/textual/issues/4782
    class SelectApp(App):
        def compose(self) -> ComposeResult:
            self.select = Select((line, line) for line in LINES)
            self.select.watch_value = self.on_select
            yield Header()
            yield self.select

        def on_select(self):
            self.select.remove()

    app = SelectApp()
    async with app.run_test() as pilot:
        await pilot.press("enter", "down", "down", "enter")
