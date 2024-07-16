from textual import on
from textual.app import App
from textual.widgets import Select
from textual.widgets._select import SelectOverlay


class SelectApp(App[None]):
    def __init__(self):
        self.changed_messages = []
        super().__init__()

    def compose(self):
        yield Select[int]([(str(n), n) for n in range(3)])

    @on(Select.Changed)
    def add_message(self, event):
        self.changed_messages.append(event)


async def test_message_control():
    app = SelectApp()
    async with app.run_test() as pilot:
        await pilot.click(Select)
        await pilot.click(SelectOverlay, offset=(2, 3))
        await pilot.pause()
        message = app.changed_messages[0]
        assert message.control is app.query_one(Select)


async def test_selecting_posts_message():
    app = SelectApp()
    async with app.run_test() as pilot:
        await pilot.click(Select)
        # Click on the 1.
        await pilot.click(SelectOverlay, offset=(2, 3))
        await pilot.pause()
        assert len(app.changed_messages) == 1
        await pilot.click(Select)
        # Click on the 2.
        await pilot.click(SelectOverlay, offset=(2, 4))
        await pilot.pause()
        assert len(app.changed_messages) == 2


async def test_same_selection_does_not_post_message():
    app = SelectApp()
    async with app.run_test() as pilot:
        await pilot.click(Select)
        # Click on the 1.
        await pilot.click(SelectOverlay, offset=(2, 3))
        await pilot.pause()
        assert len(app.changed_messages) == 1
        await pilot.click(Select)
        # Click on the 1 again...
        await pilot.click(SelectOverlay, offset=(2, 3))
        await pilot.pause()
        assert len(app.changed_messages) == 1


async def test_setting_value_posts_message() -> None:
    """Setting the value of a Select should post a message."""

    async with (app := SelectApp()).run_test() as pilot:
        assert len(app.changed_messages) == 0
        app.query_one(Select).value = 2
        await pilot.pause()
        assert len(app.changed_messages) == 1
