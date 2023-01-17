import pytest

from textual.app import App
from textual.screen import Screen
from textual.widget import Widget


class Focusable(Widget, can_focus=True):
    pass


class NonFocusable(Widget, can_focus=False, can_focus_children=False):
    pass


class ChildrenFocusableOnly(Widget, can_focus=False, can_focus_children=True):
    pass


@pytest.fixture
def screen() -> Screen:
    app = App()
    app._set_active()
    app.push_screen(Screen())

    screen = app.screen

    # The classes even/odd alternate along the focus chain.
    # The classes in/out identify nested widgets.
    screen._add_children(
        Focusable(id="foo", classes="a"),
        NonFocusable(id="bar"),
        Focusable(Focusable(id="Paul", classes="c"), id="container1", classes="b"),
        NonFocusable(Focusable(id="Jessica", classes="a"), id="container2"),
        Focusable(id="baz", classes="b"),
        ChildrenFocusableOnly(Focusable(id="child", classes="c")),
    )

    return screen


def test_focus_chain():
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
        ChildrenFocusableOnly(Focusable(id="child")),
    )

    focus_chain = [widget.id for widget in screen.focus_chain]
    assert focus_chain == ["foo", "container1", "Paul", "baz", "child"]


def test_focus_next_and_previous(screen: Screen):
    assert screen.focus_next().id == "foo"
    assert screen.focus_next().id == "container1"
    assert screen.focus_next().id == "Paul"
    assert screen.focus_next().id == "baz"
    assert screen.focus_next().id == "child"

    assert screen.focus_previous().id == "baz"
    assert screen.focus_previous().id == "Paul"
    assert screen.focus_previous().id == "container1"
    assert screen.focus_previous().id == "foo"


def test_focus_next_and_previous_with_type_selector(screen: Screen):
    """Move focus with a selector that matches the currently focused node."""
    screen.set_focus(screen.query_one("#Paul"))
    assert screen.focused.id == "Paul"

    assert screen.focus_next(Focusable).id == "Jessica"
    assert screen.focus_next(Focusable).id == "baz"
    assert screen.focus_next(Focusable).id == "child"

    assert screen.focus_previous(Focusable).id == "baz"
    assert screen.focus_previous(Focusable).id == "Jessica"
    assert screen.focus_previous(Focusable).id == "Paul"
    assert screen.focus_previous(Focusable).id == "container1"
    assert screen.focus_previous(Focusable).id == "foo"


def test_focus_next_and_previous_with_str_selector(screen: Screen):
    """Move focus with a selector that matches the currently focused node."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_next(".a").id == "Jessica"
    assert screen.focus_next("Focusable").id == "baz"

    assert screen.focus_previous(".b").id == "container1"

    assert screen.focus_next("Focusable").id == "Paul"
    assert screen.focus_next(".c").id == "child"

    assert screen.focus_previous(".c").id == "Paul"


def test_focus_next_and_previous_with_type_selector_without_self():
    """Test moving the focus with a selector that does not match the currently focused node."""
    app = App()
    app._set_active()
    app.push_screen(Screen())

    screen = app.screen

    from textual.containers import Horizontal, Vertical
    from textual.widgets import Input, Label, Static

    screen._add_children(
        Vertical(
            Horizontal(
                Input(id="w3"),
                Label(id="w4"),
                Input(id="w5"),
                Static(id="w6"),
                Label(id="w7"),
                id="w2",
            ),
            Horizontal(
                Static(id="w9"),
                Label(id="w10"),
                Static(id="w11"),
                Input(id="w12"),
                Input(id="w13"),
                id="w8",
            ),
            id="w1",
        )
    )

    screen.set_focus(screen.query_one("#w3"))
    assert screen.focused.id == "w3"

    assert screen.focus_next(Static).id == "w6"
    assert screen.focus_next(Label).id == "w7"
    assert screen.focus_next(Input).id == "w12"

    assert screen.focus_previous(Static).id == "w11"
    assert screen.focus_previous(Label).id == "w10"
    assert screen.focus_previous(Static).id == "w9"
    assert screen.focus_previous(Input).id == "w5"


def test_focus_next_and_previous_with_str_selector_without_self(screen: Screen):
    """Test moving the focus with a selector that does not match the currently focused node."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_next(".c").id == "Paul"
    assert screen.focus_next(".b").id == "baz"
    assert screen.focus_next(".c").id == "child"

    assert screen.focus_previous(".a").id == "Jessica"
    assert screen.focus_previous(".b").id == "container1"
    assert screen.focus_previous(".a").id == "foo"
