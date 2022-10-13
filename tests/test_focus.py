from textual.app import App
from textual.screen import Screen
from textual.widget import Widget


class Focusable(Widget, can_focus=True):
    pass


class NonFocusable(Widget, can_focus=False, can_focus_children=False):
    pass


async def test_focus_chain():
    app = App()
    app._set_active()
    app.push_screen(Screen())

    screen = app.screen

    # Check empty focus chain
    assert not screen.focus_chain

    app.screen._add_children(
        Focusable(id="foo"),
        NonFocusable(id="bar"),
        Focusable(Focusable(id="Paul"), id="container1"),
        NonFocusable(Focusable(id="Jessica"), id="container2"),
        Focusable(id="baz"),
    )

    focused = [widget.id for widget in screen.focus_chain]
    assert focused == ["foo", "Paul", "baz"]


async def test_focus_next_and_previous():
    app = App()
    app._set_active()
    app.push_screen(Screen())

    screen = app.screen

    screen._add_children(
        Focusable(id="foo"),
        NonFocusable(id="bar"),
        Focusable(Focusable(id="Paul"), id="container1"),
        NonFocusable(Focusable(id="Jessica"), id="container2"),
        Focusable(id="baz"),
    )

    assert screen.focus_next().id == "foo"
    assert screen.focus_next().id == "Paul"
    assert screen.focus_next().id == "baz"

    assert screen.focus_previous().id == "Paul"
    assert screen.focus_previous().id == "foo"
