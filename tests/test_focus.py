import pytest

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Label


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


def test_allow_focus():
    """Test allow_focus and allow_focus_children are called and the result used."""
    focusable_allow_focus_called = False
    non_focusable_allow_focus_called = False

    class Focusable(Widget, can_focus=False):
        def allow_focus(self) -> bool:
            nonlocal focusable_allow_focus_called
            focusable_allow_focus_called = True
            return True

    class NonFocusable(Container, can_focus=True):
        def allow_focus(self) -> bool:
            nonlocal non_focusable_allow_focus_called
            non_focusable_allow_focus_called = True
            return False

    class FocusableContainer(Container, can_focus_children=False):
        def allow_focus_children(self) -> bool:
            return True

    class NonFocusableContainer(Container, can_focus_children=True):
        def allow_focus_children(self) -> bool:
            return False

    app = App()
    app._set_active()
    app.push_screen(Screen())

    app.screen._add_children(
        Focusable(id="foo"),
        NonFocusable(id="bar"),
        FocusableContainer(Button("egg", id="egg")),
        NonFocusableContainer(Button("EGG", id="qux")),
    )
    assert [widget.id for widget in app.screen.focus_chain] == ["foo", "egg"]
    assert focusable_allow_focus_called
    assert non_focusable_allow_focus_called


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
    assert screen.focus_next("#bananas") is None
    assert screen.focused is None

    screen.set_focus(screen.query_one("#foo"))
    assert screen.focused is not None
    assert screen.focus_previous("#bananas") is None
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

    from textual.containers import Horizontal, VerticalScroll
    from textual.widgets import Button, Input, Switch

    screen._add_children(
        VerticalScroll(
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


async def test_focus_does_not_move_to_invisible_widgets():
    """Make sure invisible widgets don't get focused by accident.

    This is kind of a regression test for https://github.com/Textualize/textual/issues/3053,
    but not really.
    """

    class MyApp(App):
        CSS = "#inv { visibility: hidden; }"

        def compose(self):
            yield Button("one", id="one")
            yield Button("two", id="inv")
            yield Button("three", id="three")

    app = MyApp()
    async with app.run_test():
        assert app.focused.id == "one"
        assert app.screen.focus_next().id == "three"


async def test_focus_moves_to_visible_widgets_inside_invisible_containers():
    """Regression test for https://github.com/Textualize/textual/issues/3053."""

    class MyApp(App):
        CSS = """
        #inv { visibility: hidden; }
        #three { visibility: visible; }
        """

        def compose(self):
            yield Button(id="one")
            with Container(id="inv"):
                yield Button(id="three")

    app = MyApp()
    async with app.run_test():
        assert app.focused.id == "one"
        assert app.screen.focus_next().id == "three"


async def test_focus_chain_handles_inherited_visibility():
    """Regression test for https://github.com/Textualize/textual/issues/3053

    This is more or less a test for the interactions between #3053 and #3071.
    We want to make sure that the focus chain is computed correctly when going through
    a DOM with containers with all sorts of visibilities set.
    """

    class W(Widget):
        can_focus = True

    w1 = W(id="one")
    c2 = Container(id="two")
    w3 = W(id="three")
    c4 = Container(id="four")
    w5 = W(id="five")
    c6 = Container(id="six")
    w7 = W(id="seven")
    c8 = Container(id="eight")
    w9 = W(id="nine")
    w10 = W(id="ten")
    w11 = W(id="eleven")
    w12 = W(id="twelve")
    w13 = W(id="thirteen")

    class InheritedVisibilityApp(App[None]):
        CSS = """
        #four, #eight, #ten {
            visibility: visible;
        }

        #six, #thirteen {
            visibility: hidden;
        }
        """

        def compose(self):
            yield w1  # visible, inherited
            with c2:  # visible, inherited
                yield w3  # visible, inherited
                with c4:  # visible, set
                    yield w5  # visible, inherited
                    with c6:  # hidden, set
                        yield w7  # hidden, inherited
                        with c8:  # visible, set
                            yield w9  # visible, inherited
                        yield w10  # visible, set
                    yield w11  # visible, inherited
                yield w12  # visible, inherited
            yield w13  # invisible, set

    app = InheritedVisibilityApp()
    async with app.run_test():
        focus_chain = app.screen.focus_chain
        assert focus_chain == [
            w1,
            w3,
            w5,
            w9,
            w10,
            w11,
            w12,
        ]


async def test_mouse_down_gives_focus():
    class MyApp(App):
        AUTO_FOCUS = None

        def compose(self):
            yield Button()

    app = MyApp()
    async with app.run_test() as pilot:
        # Sanity check.
        assert app.focused is None

        await pilot.mouse_down(Button)
        assert isinstance(app.focused, Button)


async def test_mouse_up_does_not_give_focus():
    class MyApp(App):
        AUTO_FOCUS = None

        def compose(self):
            yield Button()

    app = MyApp()
    async with app.run_test() as pilot:
        # Sanity check.
        assert app.focused is None

        await pilot.mouse_up(Button)
        assert app.focused is None


async def test_focus_pseudo_class():
    """Test focus and blue pseudo classes"""

    # https://github.com/Textualize/textual/pull/3645
    class FocusApp(App):
        AUTO_FOCUS = None

        def compose(self) -> ComposeResult:
            yield Button("Hello")

    app = FocusApp()
    async with app.run_test() as pilot:
        button = app.query_one(Button)
        classes = list(button.get_pseudo_classes())
        # Blurred, not focused
        assert "blur" in classes
        assert "focus" not in classes

        # Focus the button
        button.focus()
        await pilot.pause()

        # Focused, not blurred
        classes = list(button.get_pseudo_classes())
        assert "blur" not in classes
        assert "focus" in classes


async def test_get_focusable_widget_at() -> None:
    """Check that clicking a non-focusable widget will focus any (focusable) ancestors."""

    class FocusApp(App):
        AUTO_FOCUS = None

        def compose(self) -> ComposeResult:
            with ScrollableContainer(id="focusable"):
                with Container():
                    yield Label("Foo", id="foo")
                    yield Label("Bar", id="bar")
            yield Label("Egg", id="egg")

    app = FocusApp()
    async with app.run_test() as pilot:
        # Nothing focused
        assert app.screen.focused is None
        # Click foo
        await pilot.click("#foo")
        # Confirm container is focused
        assert app.screen.focused is not None
        assert app.screen.focused.id == "focusable"
        # Reset focus
        app.screen.set_focus(None)
        assert app.screen.focused is None
        # Click bar
        await pilot.click("#bar")
        # Confirm container is focused
        assert app.screen.focused is not None
        assert app.screen.focused.id == "focusable"
        # Reset focus
        app.screen.set_focus(None)
        assert app.screen.focused is None
        # Click egg (outside of focusable widget)
        await pilot.click("#egg")
        # Confirm nothing focused
        assert app.screen.focused is None
