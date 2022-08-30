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

    # Check empty focus chain
    assert not app.focus_chain

    app.screen._add_children(
        Focusable(id="foo"),
        NonFocusable(id="bar"),
        Focusable(Focusable(id="Paul"), id="container1"),
        NonFocusable(Focusable(id="Jessica"), id="container2"),
        Focusable(id="baz"),
    )

    focused = [widget.id for widget in app.focus_chain]
    assert focused == ["foo", "Paul", "baz"]


async def test_focus_next_and_previous():

    app = App()
    app._set_active()
    app.push_screen(Screen())
    app.screen._add_children(
        Focusable(id="foo"),
        NonFocusable(id="bar"),
        Focusable(Focusable(id="Paul"), id="container1"),
        NonFocusable(Focusable(id="Jessica"), id="container2"),
        Focusable(id="baz"),
    )

    assert app.focus_next().id == "foo"
    assert app.focus_next().id == "Paul"
    assert app.focus_next().id == "baz"

    assert app.focus_previous().id == "Paul"
    assert app.focus_previous().id == "foo"
