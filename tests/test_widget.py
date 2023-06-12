import pytest
from rich.text import Text

from textual import events
from textual._node_list import DuplicateIds
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.errors import StyleValueError
from textual.css.query import NoMatches
from textual.geometry import Offset, Size
from textual.message import Message
from textual.widget import MountError, PseudoClasses, Widget
from textual.widgets import Label


@pytest.mark.parametrize(
    "set_val, get_val, style_str",
    [
        [True, True, "visible"],
        [False, False, "hidden"],
        ["hidden", False, "hidden"],
        ["visible", True, "visible"],
    ],
)
def test_widget_set_visible_true(set_val, get_val, style_str):
    widget = Widget()
    widget.visible = set_val

    assert widget.visible is get_val
    assert widget.styles.visibility == style_str


def test_widget_set_visible_invalid_string():
    widget = Widget()

    with pytest.raises(StyleValueError):
        widget.visible = "nope! no widget for me!"

    assert widget.visible


def test_widget_content_width():
    class TextWidget(Widget):
        def __init__(self, text: str, id: str) -> None:
            self.text = text
            super().__init__(id=id)
            self.expand = False
            self.shrink = True

        def render(self) -> str:
            return self.text

    widget1 = TextWidget("foo", id="widget1")
    widget2 = TextWidget("foo\nbar", id="widget2")
    widget3 = TextWidget("foo\nbar\nbaz", id="widget3")

    app = App()
    app._set_active()

    width = widget1.get_content_width(Size(20, 20), Size(80, 24))
    height = widget1.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 1

    width = widget2.get_content_width(Size(20, 20), Size(80, 24))
    height = widget2.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 2

    width = widget3.get_content_width(Size(20, 20), Size(80, 24))
    height = widget3.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 3


class GetByIdApp(App):
    def compose(self) -> ComposeResult:
        grandchild1 = Widget(id="grandchild1")
        child1 = Widget(grandchild1, id="child1")
        child2 = Widget(id="child2")

        yield Widget(
            child1,
            child2,
            id="parent",
        )


@pytest.fixture
async def hierarchy_app():
    app = GetByIdApp()
    async with app.run_test():
        yield app


@pytest.fixture
async def parent(hierarchy_app):
    yield hierarchy_app.get_widget_by_id("parent")


def test_get_child_by_id_gets_first_child(parent):
    child = parent.get_child_by_id(id="child1")
    assert child.id == "child1"
    assert child.get_child_by_id(id="grandchild1").id == "grandchild1"
    assert parent.get_child_by_id(id="child2").id == "child2"


def test_get_child_by_id_no_matching_child(parent):
    with pytest.raises(NoMatches):
        parent.get_child_by_id(id="doesnt-exist")


def test_get_child_by_id_only_immediate_descendents(parent):
    with pytest.raises(NoMatches):
        parent.get_child_by_id(id="grandchild1")


async def test_get_child_by_type():
    class GetChildApp(App):
        def compose(self) -> ComposeResult:
            yield Widget(id="widget1")
            yield Container(
                Label(id="label1"),
                Widget(id="widget2"),
                id="container1",
            )

    app = GetChildApp()
    async with app.run_test():
        assert app.get_child_by_type(Widget).id == "widget1"
        assert app.get_child_by_type(Container).id == "container1"
        with pytest.raises(NoMatches):
            app.get_child_by_type(Label)


def test_get_widget_by_id_no_matching_child(parent):
    with pytest.raises(NoMatches):
        parent.get_widget_by_id(id="i-dont-exist")


def test_get_widget_by_id_non_immediate_descendants(parent):
    result = parent.get_widget_by_id("grandchild1")
    assert result.id == "grandchild1"


def test_get_widget_by_id_immediate_descendants(parent):
    result = parent.get_widget_by_id("child1")
    assert result.id == "child1"


def test_get_widget_by_id_doesnt_return_self(parent):
    with pytest.raises(NoMatches):
        parent.get_widget_by_id("parent")


def test_get_widgets_app_delegated(hierarchy_app, parent):
    # Check that get_child_by_id finds the parent, which is a child of the default Screen
    queried_parent = hierarchy_app.get_child_by_id("parent")
    assert queried_parent is parent

    # Check that the grandchild (descendant of the default screen) is found
    grandchild = hierarchy_app.get_widget_by_id("grandchild1")
    assert grandchild.id == "grandchild1"


def test_widget_mount_ids_must_be_unique_mounting_all_in_one_go(parent):
    widget1 = Widget(id="hello")
    widget2 = Widget(id="hello")

    with pytest.raises(MountError):
        parent.mount(widget1, widget2)


def test_widget_mount_ids_must_be_unique_mounting_multiple_calls(parent):
    widget1 = Widget(id="hello")
    widget2 = Widget(id="hello")

    parent.mount(widget1)
    with pytest.raises(DuplicateIds):
        parent.mount(widget2)


def test_get_pseudo_class_state():
    widget = Widget()
    pseudo_classes = widget.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=True, focus=False, hover=False)


def test_get_pseudo_class_state_disabled():
    widget = Widget(disabled=True)
    pseudo_classes = widget.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=False, focus=False, hover=False)


def test_get_pseudo_class_state_parent_disabled():
    child = Widget()
    _parent = Widget(child, disabled=True)
    pseudo_classes = child.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=False, focus=False, hover=False)


def test_get_pseudo_class_state_hover():
    widget = Widget()
    widget.mouse_over = True
    pseudo_classes = widget.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=True, focus=False, hover=True)


def test_get_pseudo_class_state_focus():
    widget = Widget()
    widget.has_focus = True
    pseudo_classes = widget.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=True, focus=True, hover=False)


# Regression test for https://github.com/Textualize/textual/issues/1634
async def test_remove():
    class RemoveMeLabel(Label):
        async def on_mount(self) -> None:
            await self.run_action("app.remove_all")

    class Container(Widget):
        async def clear(self) -> None:
            await self.query("*").remove()

    class RemoveApp(App):
        def compose(self) -> ComposeResult:
            yield Container(RemoveMeLabel())

        async def action_remove_all(self) -> None:
            await self.query_one(Container).clear()
            self.exit(123)

    app = RemoveApp()
    async with app.run_test() as pilot:
        await pilot.press("r")
        await pilot.pause()
    assert app.return_value == 123


# Regression test for https://github.com/Textualize/textual/issues/2079
async def test_remove_unmounted():
    mounted = False

    class RemoveApp(App):
        def on_mount(self):
            nonlocal mounted
            label = Label()
            label.remove()
            mounted = True

    app = RemoveApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert mounted


def test_render_str() -> None:
    widget = Label()
    assert widget.render_str("foo") == Text("foo")
    assert widget.render_str("[b]foo") == Text.from_markup("[b]foo")
    # Text objects are passed unchanged
    text = Text("bar")
    assert widget.render_str(text) is text


async def test_compose_order() -> None:
    from textual.containers import Horizontal
    from textual.screen import Screen
    from textual.widgets import Select

    class MyScreen(Screen):
        def on_mount(self) -> None:
            self.query_one(Select).value = 1

        def compose(self) -> ComposeResult:
            yield Horizontal(
                Select(((str(n), n) for n in range(10)), id="select"),
                id="screen-horizontal",
            )

    class SelectBugApp(App[None]):
        async def on_mount(self):
            await self.push_screen(MyScreen(id="my-screen"))
            self.query_one(Select)

    app = SelectBugApp()
    messages: list[Message] = []

    async with app.run_test(message_hook=messages.append) as pilot:
        await pilot.pause()

    mounts = [
        message._sender.id
        for message in messages
        if isinstance(message, events.Mount) and message._sender.id is not None
    ]

    expected = [
        "_default",  # default  screen
        "label",  # A static in select
        "select",  # The select
        "screen-horizontal",  # The horizontal in MyScreen.compose
        "my-screen",  # THe screen mounted in the app
    ]

    assert mounts == expected


def test_children_must_be_widgets():
    with pytest.raises(TypeError):
        Widget(1, 2, 3)


def test_orphan_widget_has_no_siblings():
    assert Widget().siblings == []


def test__allow_scroll_default():
    assert not Widget()._allow_scroll


async def test__allow_scroll():
    from textual.containers import ScrollableContainer

    class AllowScrollApp(App):
        CSS = "ScrollableContainer { width: 3; height: 3; }"

        def compose(self):
            with ScrollableContainer():
                yield Label("This is\n\n\n\n\nlarge text.")

    app = AllowScrollApp()
    async with app.run_test():
        assert app.query_one(ScrollableContainer)._allow_scroll


async def test_offset_getter_setter():
    class OffsetApp(App):
        def compose(self):
            yield Label("hello")

    app = OffsetApp()
    async with app.run_test():
        label = app.query_one(Label)
        assert label.offset == Offset(0, 0)
        label.offset = (7, 3)
        assert label.offset == Offset(7, 3)


def test_get_set_tooltip():
    widget = Widget()
    assert widget.tooltip is None
    widget.tooltip = "This is a tooltip."
    assert widget.tooltip == "This is a tooltip."


