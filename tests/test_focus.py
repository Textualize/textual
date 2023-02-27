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


def test_focus_next_wrap_around(screen: Screen):
    """Ensure focusing the next widget wraps around the focus chain."""
    screen.set_focus(screen.query_one("#child"))
    assert screen.focused.id == "child"

    assert screen.focus_next().id == "foo"


def test_focus_previous_wrap_around(screen: Screen):
    """Ensure focusing the previous widget wraps around the focus chain."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_previous().id == "child"


def test_wrap_around_selector(screen: Screen):
    """Ensure moving focus in both directions wraps around the focus chain."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_previous("#Paul").id == "Paul"
    assert screen.focus_next("#foo").id == "foo"


def test_no_focus_empty_selector(screen: Screen):
    """Ensure focus is cleared when selector matches nothing."""
    assert screen.focus_next("#bananas") is None
    assert screen.focus_previous("#bananas") is None

    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused is not None
    assert screen.focus_next("bananas") is None
    assert screen.focused is None

    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused is not None
    assert screen.focus_previous("bananas") is None
    assert screen.focused is None


def test_focus_next_and_previous_with_type_selector(screen: Screen):
    """Move focus with a selector that matches the currently focused node."""
    screen.set_focus(screen.query_one("#Paul"))
    assert screen.focused.id == "Paul"

    assert screen.focus_next(Focusable).id == "baz"
    assert screen.focus_next(Focusable).id == "child"

    assert screen.focus_previous(Focusable).id == "baz"
    assert screen.focus_previous(Focusable).id == "Paul"
    assert screen.focus_previous(Focusable).id == "container1"
    assert screen.focus_previous(Focusable).id == "foo"


def test_focus_next_and_previous_with_str_selector(screen: Screen):
    """Move focus with a selector that matches the currently focused node."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_next(".a").id == "foo"
    assert screen.focus_next(".c").id == "Paul"
    assert screen.focus_next(".c").id == "child"

    assert screen.focus_previous(".c").id == "Paul"
    assert screen.focus_previous(".a").id == "foo"


def test_focus_next_and_previous_with_type_selector_without_self():
    """Test moving the focus with a selector that does not match the currently focused node."""
    app = App()
    app._set_active()
    app.push_screen(Screen())

    screen = app.screen

    from textual.containers import Horizontal, Vertical
    from textual.widgets import Button, Input, Switch

    screen._add_children(
        Vertical(
            Horizontal(
                Input(id="w3"),
                Switch(id="w4"),
                Input(id="w5"),
                Button(id="w6"),
                Switch(id="w7"),
                id="w2",
            ),
            Horizontal(
                Button(id="w9"),
                Switch(id="w10"),
                Button(id="w11"),
                Input(id="w12"),
                Input(id="w13"),
                id="w8",
            ),
            id="w1",
        )
    )

    screen.set_focus(screen.query_one("#w3"))
    assert screen.focused.id == "w3"

    assert screen.focus_next(Button).id == "w6"
    assert screen.focus_next(Switch).id == "w7"
    assert screen.focus_next(Input).id == "w12"

    assert screen.focus_previous(Button).id == "w11"
    assert screen.focus_previous(Switch).id == "w10"
    assert screen.focus_previous(Button).id == "w9"
    assert screen.focus_previous(Input).id == "w5"


def test_focus_next_and_previous_with_str_selector_without_self(screen: Screen):
    """Test moving the focus with a selector that does not match the currently focused node."""
    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused.id == "foo"

    assert screen.focus_next(".c").id == "Paul"
    assert screen.focus_next(".b").id == "baz"
    assert screen.focus_next(".c").id == "child"

    assert screen.focus_previous(".a").id == "foo"
    assert screen.focus_previous(".a").id == "foo"
    assert screen.focus_previous(".b").id == "baz"
