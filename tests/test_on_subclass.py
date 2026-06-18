"""Tests for Textualize/textual#4968: @on decorator should respect subclass
boundaries when matching message types.

In Textual, a Button subclass like MyButton(Button) inherits the parent's
nested `Pressed` message class because Python does not inherit nested
classes. This means `@on(MyButton.Pressed)` and `@on(Button.Pressed)` end
up registering handlers against the same message class, so a regular
Button click wrongly fires handlers written for MyButton.

The fix (Button.__init_subclass__): every Button subclass gets its own
Pressed message class, distinct from Button.Pressed. handler_name is
preserved so existing on_button_pressed naming-convention handlers keep
working.
"""

import pytest
from textual import on
from textual.app import App
from textual.widgets import Button


class MyButton(Button):
    pass


class _App_BaseClickFiresSubclassHandler(App[None]):
    """@on(MyButton.Pressed) should NOT fire when a regular Button is clicked."""

    def __init__(self):
        super().__init__()
        self.subclass_fired = 0
        self.base_fired = 0

    def compose(self):
        yield Button("Normal Button")

    @on(MyButton.Pressed)
    def on_my_button_pressed(self) -> None:
        self.subclass_fired += 1

    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        self.base_fired += 1


class _App_SubclassClickFiresBothHandlers(App[None]):
    """When MyButton is clicked, both @on(MyButton.Pressed) and
    @on(Button.Pressed) (since MyButton is-a Button) should fire."""

    def __init__(self):
        super().__init__()
        self.subclass_fired = 0
        self.base_fired = 0

    def compose(self):
        yield MyButton("My Button")

    @on(MyButton.Pressed)
    def on_my_button_pressed(self) -> None:
        self.subclass_fired += 1

    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        self.base_fired += 1


@pytest.mark.asyncio
async def test_4968_base_button_click_does_not_fire_subclass_on_handler():
    app = _App_BaseClickFiresSubclassHandler()
    async with app.run_test() as pilot:
        btn = pilot.app.query_one(Button)
        await pilot.click(btn)
        await pilot.pause()
        assert app.base_fired == 1, (
            "regular Button click should fire @on(Button.Pressed)"
        )
        assert app.subclass_fired == 0, (
            "@on(MyButton.Pressed) must not fire for a regular Button click (bug #4968)"
        )


@pytest.mark.asyncio
async def test_subclass_button_click_fires_subclass_on_handler():
    app = _App_SubclassClickFiresBothHandlers()
    async with app.run_test() as pilot:
        btn = pilot.app.query_one(MyButton)
        await pilot.click(btn)
        await pilot.pause()
        # Both should fire: MyButton IS-A Button, so @on(Button.Pressed)
        # matches too via MRO walking.
        assert app.subclass_fired == 1, (
            "@on(MyButton.Pressed) should fire when MyButton is clicked"
        )
        assert app.base_fired == 1, (
            "@on(Button.Pressed) should also fire (MyButton is-a Button)"
        )


def test_button_subclass_pressed_classes_are_distinct():
    """Sanity: each Button subclass should get its own Pressed class."""
    assert MyButton.Pressed is not Button.Pressed
    assert issubclass(MyButton.Pressed, Button.Pressed)
    # handler_name is preserved so on_button_pressed naming-convention still matches
    assert (
        MyButton.Pressed.handler_name
        == Button.Pressed.handler_name
        == "on_button_pressed"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
