from rich.console import Console

from textual.app import App
from textual.widgets import Input


async def test_input_value_visible_on_instantiation():
    """Check if the full input value is rendered if the input is instantiated with it."""

    class MyApp(App):
        def compose(self):
            yield Input(value="value")

    app = MyApp()
    async with app.run_test():
        console = Console(width=5)
        with console.capture() as capture:
            console.print(app.query_one(Input).render())
        assert capture.get() == "value"


async def test_input_value_visible_after_value_assignment():
    """Check if the full input value is rendered if the value is assigned to programmatically."""

    class MyApp(App):
        def compose(self):
            yield Input()

        def on_mount(self):
            self.query_one(Input).value = "value"

    app = MyApp()
    async with app.run_test():
        console = Console(width=5)
        with console.capture() as capture:
            console.print(app.query_one(Input).render())
        assert capture.get() == "value"


async def test_input_value_visible_if_mounted_later():
    """Check if full input value is rendered if the widget is mounted later."""

    class MyApp(App):
        BINDINGS = [("a", "add_input", "add_input")]

        async def action_add_input(self):
            await self.mount(Input(value="value"))

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        console = Console(width=5)
        with console.capture() as capture:
            console.print(app.query_one(Input).render())
        assert capture.get() == "value"


async def test_input_value_visible_if_mounted_later_and_focused():
    """Check if full input value is rendered if the widget is mounted later and immediately focused."""

    class MyApp(App):
        BINDINGS = [("a", "add_input", "add_input")]

        async def action_add_input(self):
            inp = Input(value="value")
            await self.mount(inp)
            inp.focus()

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        console = Console(width=5)
        with console.capture() as capture:
            console.print(app.query_one(Input).render())
        assert capture.get() == "value"


async def test_input_value_visible_if_mounted_later_and_assigned_after():
    """Check if full value rendered if the widget is mounted later and the value is then assigned to."""

    class MyApp(App):
        BINDINGS = [
            ("a", "add_input", "add_input"),
            ("v", "set_value", "set_value"),
        ]

        async def action_add_input(self):
            await self.mount(Input())

        def action_set_value(self):
            self.query_one(Input).value = "value"

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("v")
        console = Console(width=5)
        with console.capture() as capture:
            console.print(app.query_one(Input).render())
        assert capture.get() == "value"
