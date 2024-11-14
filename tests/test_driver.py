from textual import on
from textual.app import App
from textual.events import Click, MouseDown, MouseUp
from textual.widgets import Button


async def test_driver_mouse_down_up_click():
    """Mouse down and up should issue a click."""

    class MyApp(App):
        messages = []

        @on(Click)
        @on(MouseDown)
        @on(MouseUp)
        def handle(self, event):
            self.messages.append(event)

    app = MyApp()
    async with app.run_test() as pilot:
        app._driver.process_message(MouseDown(None, 0, 0, 0, 0, 1, False, False, False))
        app._driver.process_message(MouseUp(None, 0, 0, 0, 0, 1, False, False, False))
        await pilot.pause()
        assert len(app.messages) == 3
        assert isinstance(app.messages[0], MouseDown)
        assert isinstance(app.messages[1], MouseUp)
        assert isinstance(app.messages[2], Click)


async def test_driver_mouse_down_up_click_widget():
    """Mouse down and up should issue a click when they're on a widget."""

    class MyApp(App):
        messages = []

        def compose(self):
            yield Button()

        def on_button_pressed(self, event):
            self.messages.append(event)

    app = MyApp()
    async with app.run_test() as pilot:
        app._driver.process_message(MouseDown(None, 0, 0, 0, 0, 1, False, False, False))
        app._driver.process_message(MouseUp(None, 0, 0, 0, 0, 1, False, False, False))
        await pilot.pause()
        assert len(app.messages) == 1


async def test_driver_mouse_down_drag_inside_widget_up_click():
    """Mouse down and up should issue a click, even if the mouse moves but remains
    inside the same widget."""

    class MyApp(App):
        messages = []

        def compose(self):
            yield Button()

        def on_button_pressed(self, event):
            self.messages.append(event)

    app = MyApp()
    button_width = 16
    button_height = 3
    async with app.run_test() as pilot:
        # Sanity check
        width, height = app.query_one(Button).region.size
        assert (width, height) == (button_width, button_height)

        # Mouse down on the button, then move the mouse inside the button, then mouse up.
        app._driver.process_message(MouseDown(None, 0, 0, 0, 0, 1, False, False, False))
        app._driver.process_message(
            MouseUp(
                None,
                button_width - 1,
                button_height - 1,
                button_width - 1,
                button_height - 1,
                1,
                False,
                False,
                False,
            )
        )
        await pilot.pause()
        # A click should still be triggered.
        assert len(app.messages) == 1


async def test_driver_mouse_down_drag_outside_widget_up_click():
    """Mouse down and up don't issue a click if the mouse moves outside of the initial widget."""

    class MyApp(App):
        messages = []

        def compose(self):
            yield Button()

        def on_button_pressed(self, event):
            self.messages.append(event)

    app = MyApp()
    button_width = 16
    button_height = 3
    async with app.run_test() as pilot:
        # Sanity check
        width, height = app.query_one(Button).region.size
        assert (width, height) == (button_width, button_height)

        # Mouse down on the button, then move the mouse outside the button, then mouse up.
        app._driver.process_message(MouseDown(None, 0, 0, 0, 0, 1, False, False, False))
        app._driver.process_message(
            MouseUp(
                None,
                button_width + 1,
                button_height + 1,
                button_width + 1,
                button_height + 1,
                1,
                False,
                False,
                False,
            )
        )
        await pilot.pause()
        assert len(app.messages) == 0
