import pytest

from textual import on
from textual._on import OnDecoratorError
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, TabbedContent, TabPane


async def test_on_button_pressed() -> None:
    """Test handlers with @on decorator."""

    pressed: list[str] = []

    class ButtonApp(App):
        def compose(self) -> ComposeResult:
            yield Button("OK", id="ok")
            yield Button("Cancel", classes="exit cancel")
            yield Button("Quit", classes="exit quit")

        @on(Button.Pressed, "#ok")
        def ok(self):
            pressed.append("ok")

        @on(Button.Pressed, ".exit")
        def exit(self):
            pressed.append("exit")

        @on(Button.Pressed, ".exit.quit")
        def _(self):
            pressed.append("quit")

        def on_button_pressed(self):
            pressed.append("default")

    app = ButtonApp()
    async with app.run_test() as pilot:
        await pilot.press("tab", "enter", "tab", "enter", "tab", "enter")
        await pilot.pause()

    assert pressed == [
        "ok",  # Matched ok first
        "default",  # on_button_pressed matched everything
        "exit",  # Cancel button, matches exit
        "default",  # on_button_pressed matched everything
        "exit",  # Quit button pressed, matched exit and _
        "quit",  # Matched previous button
        "default",  # on_button_pressed matched everything
    ]


async def test_on_inheritance() -> None:
    """Test on decorator and inheritance."""
    pressed: list[str] = []

    class MyWidget(Widget):
        def compose(self) -> ComposeResult:
            yield Button("OK", id="ok")

        # Also called
        @on(Button.Pressed, "#ok")
        def ok(self):
            pressed.append("MyWidget.ok base")

    class DerivedWidget(MyWidget):
        # Should be called first
        @on(Button.Pressed, "#ok")
        def ok(self):
            pressed.append("MyWidget.ok derived")

    class ButtonApp(App):
        def compose(self) -> ComposeResult:
            yield DerivedWidget()

    app = ButtonApp()
    async with app.run_test() as pilot:
        await pilot.press("tab", "enter")

    expected = ["MyWidget.ok derived", "MyWidget.ok base"]
    assert pressed == expected


def test_on_bad_selector() -> None:
    """Check bad selectors raise an error."""

    with pytest.raises(OnDecoratorError):

        @on(Button.Pressed, "@")
        def foo():
            pass


def test_on_no_control() -> None:
    """Check messages with no 'control' attribute raise an error."""

    class CustomMessage(Message):
        pass

    with pytest.raises(OnDecoratorError):

        @on(CustomMessage, "#foo")
        def foo():
            pass


def test_on_attribute_not_listed() -> None:
    """Check `on` checks if the attribute is in ALLOW_SELECTOR_MATCH."""

    class CustomMessage(Message):
        pass

    with pytest.raises(OnDecoratorError):

        @on(CustomMessage, foo="bar")
        def foo():
            pass


async def test_on_arbitrary_attributes() -> None:
    log: list[str] = []

    class OnArbitraryAttributesApp(App[None]):
        def compose(self) -> ComposeResult:
            with TabbedContent():
                yield TabPane("One", id="one")
                yield TabPane("Two", id="two")
                yield TabPane("Three", id="three")

        def on_mount(self) -> None:
            self.query_one(TabbedContent).add_class("tabs")

        @on(TabbedContent.TabActivated, tab="#one")
        def one(self) -> None:
            log.append("one")

        @on(TabbedContent.TabActivated, ".tabs", tab="#two")
        def two(self) -> None:
            log.append("two")

    app = OnArbitraryAttributesApp()
    async with app.run_test() as pilot:
        await pilot.press("tab", "right", "right")

    assert log == ["one", "two"]
