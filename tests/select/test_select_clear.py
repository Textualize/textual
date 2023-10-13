from textual.app import App, ComposeResult
from textual.widgets import Select


class SelectApp(App[None]):
    INITIAL_VALUE = 3

    def compose(self) -> ComposeResult:
        yield Select[int]([(str(n), n) for n in range(10)],
                          value=self.INITIAL_VALUE)


async def test_select_clear_value():
    async with SelectApp().run_test() as pilot:
        assert pilot.app.query_one(Select).value == SelectApp.INITIAL_VALUE
        pilot.app.query_one(Select).clear()
        assert pilot.app.query_one(Select).value is None
