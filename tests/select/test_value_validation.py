from textual.app import App
from textual.widgets import Select


class SelectApp(App[None]):
    def __init__(self, initial_value=None):
        self.initial_value = initial_value
        super().__init__()

    def compose(self):
        yield Select[int]([(str(n), n) for n in range(3)], value=self.initial_value)


async def test_value_assignment_is_validated():
    app = SelectApp()
    async with app.run_test() as pilot:
        app.query_one(Select).value = "french fries"
        await pilot.pause()  # Let watchers/validators do their thing.
        assert app.query_one(Select).value is None


async def test_initial_value_is_validated():
    app = SelectApp(1)
    async with app.run_test():
        assert app.query_one(Select).value == 1
