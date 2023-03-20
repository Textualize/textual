from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget


async def test_message_inheritance_namespace():
    """Inherited messages get their correct namespaces.

    Regression test for https://github.com/Textualize/textual/issues/1814.
    """

    class BaseWidget(Widget):
        class Fired(Message):
            pass

        def trigger(self) -> None:
            self.post_message(self.Fired())

    class Left(BaseWidget):
        class Fired(BaseWidget.Fired):
            pass

    class Right(BaseWidget):
        class Fired(BaseWidget.Fired):
            pass

    handlers_called = []

    class MessageInheritanceApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Left()
            yield Right()

        def on_left_fired(self):
            handlers_called.append("left")

        def on_right_fired(self):
            handlers_called.append("right")

    app = MessageInheritanceApp()
    async with app.run_test():
        app.query_one(Left).trigger()
        app.query_one(Right).trigger()

    assert handlers_called == ["left", "right"]
