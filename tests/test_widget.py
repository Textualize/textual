from operator import attrgetter

import pytest

from textual import events
from textual._node_list import DuplicateIds
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.content import Content
from textual.css.errors import StyleValueError
from textual.css.query import NoMatches
from textual.geometry import Offset, Size
from textual.message import Message
from textual.widget import BadWidgetName, MountError, PseudoClasses, Widget
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    Log,
    OptionList,
    RichLog,
    Switch,
    TextArea,
)


async def test_widget_construct():
    """Regression test for https://github.com/Textualize/textual/issues/5042"""

    # Check that constructing the widget outside of the app, doesn't invoke code that
    # expects an active app.
    class MyApp(App):
        def __init__(self) -> None:
            super().__init__()
            self.button = Button()
            self.data_table = DataTable()
            self.footer = Footer()
            self.header = Header()
            self.input = Input()
            self.label = Label()
            self.loading_indicator = LoadingIndicator()
            self.log_ = Log()
            self.option_list = OptionList()
            self.rich_log = RichLog()
            self.switch = Switch()
            self.text_area = TextArea(language="python")

    app = MyApp()
    async with app.run_test():
        pass


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
    with app._context():
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

    @property
    def parent(self) -> Widget:
        return self.query_one("#parent")


@pytest.fixture
async def hierarchy_app():
    app = GetByIdApp()
    yield app


async def test_get_child_by_id_gets_first_child(hierarchy_app):
    async with hierarchy_app.run_test():
        parent = hierarchy_app.parent
        child = parent.get_child_by_id(id="child1")
        assert child.id == "child1"
        assert child.get_child_by_id(id="grandchild1").id == "grandchild1"
        assert parent.get_child_by_id(id="child2").id == "child2"


async def test_get_child_by_id_no_matching_child(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        with pytest.raises(NoMatches):
            parent.get_child_by_id(id="doesnt-exist")


async def test_get_child_by_id_only_immediate_descendents(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
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


async def test_get_widget_by_id_no_matching_child(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        with pytest.raises(NoMatches):
            parent.get_widget_by_id(id="i-dont-exist")


async def test_get_widget_by_id_non_immediate_descendants(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        result = parent.get_widget_by_id("grandchild1")
        assert result.id == "grandchild1"


async def test_get_widget_by_id_immediate_descendants(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        result = parent.get_widget_by_id("child1")
        assert result.id == "child1"


async def test_get_widget_by_id_doesnt_return_self(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        with pytest.raises(NoMatches):
            parent.get_widget_by_id("parent")


async def test_get_widgets_app_delegated(hierarchy_app):
    # Check that get_child_by_id finds the parent, which is a child of the default Screen
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        queried_parent = hierarchy_app.get_child_by_id("parent")
        assert queried_parent is parent

        # Check that the grandchild (descendant of the default screen) is found
        grandchild = hierarchy_app.get_widget_by_id("grandchild1")
        assert grandchild.id == "grandchild1"


async def test_widget_mount_ids_must_be_unique_mounting_all_in_one_go(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
        widget1 = Widget(id="hello")
        widget2 = Widget(id="hello")

        with pytest.raises(MountError):
            parent.mount(widget1, widget2)


async def test_widget_mount_ids_must_be_unique_mounting_multiple_calls(hierarchy_app):
    async with hierarchy_app.run_test() as pilot:
        parent = pilot.app.parent
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
    _parent = Widget(disabled=True)
    child._attach(_parent)
    pseudo_classes = child.get_pseudo_class_state()
    assert pseudo_classes == PseudoClasses(enabled=False, focus=False, hover=False)


def test_get_pseudo_class_state_hover():
    widget = Widget()
    widget.mouse_hover = True
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
    assert widget.render_str("foo") == Content("foo")
    assert widget.render_str("[b]foo") == Content.from_markup("[b]foo")
    # Text objects are passed unchanged
    content = Content("bar")
    assert widget.render_str(content) is content


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
            self.screen.query_one(Select)

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


async def test_loading():
    """Test setting the loading reactive."""

    class LoadingApp(App):
        def compose(self) -> ComposeResult:
            yield Label("Hello, World")

    async with LoadingApp().run_test() as pilot:
        app = pilot.app
        label = app.query_one(Label)
        assert label.loading == False
        assert label._cover_widget is None

        label.loading = True
        await pilot.pause()
        assert label._cover_widget is not None

        label.loading = True  # Setting to same value is a null-op
        await pilot.pause()
        assert label._cover_widget is not None

        label.loading = False
        await pilot.pause()
        assert label._cover_widget is None

        label.loading = False  # Setting to same value is a null-op
        await pilot.pause()
        assert label._cover_widget is None


async def test_loading_button():
    """Test loading indicator renders buttons unclickable."""

    counter = 0

    class LoadingApp(App):
        def compose(self) -> ComposeResult:
            yield Button("Hello, World", action="app.inc")

        def action_inc(self) -> None:
            nonlocal counter
            counter += 1

    async with LoadingApp().run_test() as pilot:
        # Sanity check
        assert counter == 0

        button = pilot.app.query_one(Button)
        button.active_effect_duration = 0

        # Click the button to advance the counter
        await pilot.click(button)
        assert counter == 1

        # Set the button to loading state
        button.loading = True

        # A click should do nothing
        await pilot.click(button)
        assert counter == 1

        # Set the button to not loading
        button.loading = False

        # Click should advance counter
        await pilot.click(button)
        assert counter == 2


async def test_is_mounted_property():
    class TestWidgetIsMountedApp(App):
        pass

    async with TestWidgetIsMountedApp().run_test() as pilot:
        widget = Widget()
        assert widget.is_mounted is False
        await pilot.app.mount(widget)
        assert widget.is_mounted is True


async def test_mount_error_not_widget():
    class NotWidgetApp(App):
        def compose(self) -> ComposeResult:
            yield {}

    app = NotWidgetApp()
    with pytest.raises(MountError):
        async with app.run_test():
            pass


async def test_mount_error_bad_widget():
    class DaftWidget(Widget):
        def __init__(self):
            # intentionally missing super()
            pass

    class NotWidgetApp(App):
        def compose(self) -> ComposeResult:
            yield DaftWidget()

    app = NotWidgetApp()
    with pytest.raises(MountError):
        async with app.run_test():
            pass


async def test_render_returns_text():
    """Test that render processes console markup when returning a string."""

    # Regression test for https://github.com/Textualize/textual/issues/3918
    class SimpleWidget(Widget):
        def render(self) -> str:
            return "Hello [b]World[/b]!"

    widget = SimpleWidget()
    render_result = widget._render()
    assert isinstance(render_result, Content)
    assert render_result.plain == "Hello World!"


async def test_sort_children() -> None:
    """Test the sort_children method."""

    class SortApp(App):
        def compose(self) -> ComposeResult:
            with Container(id="container"):
                yield Label("three", id="l3")
                yield Label("one", id="l1")
                yield Label("four", id="l4")
                yield Label("two", id="l2")

    app = SortApp()
    async with app.run_test():
        container = app.query_one("#container", Container)
        assert [label.id for label in container.query(Label)] == [
            "l3",
            "l1",
            "l4",
            "l2",
        ]
        container.sort_children(key=attrgetter("id"))
        assert [label.id for label in container.query(Label)] == [
            "l1",
            "l2",
            "l3",
            "l4",
        ]
        container.sort_children(key=attrgetter("id"), reverse=True)
        assert [label.id for label in container.query(Label)] == [
            "l4",
            "l3",
            "l2",
            "l1",
        ]


async def test_sort_children_no_key() -> None:
    """Test sorting with no key."""

    class SortApp(App):
        def compose(self) -> ComposeResult:
            with Container(id="container"):
                yield Label("three", id="l3")
                yield Label("one", id="l1")
                yield Label("four", id="l4")
                yield Label("two", id="l2")

    app = SortApp()
    async with app.run_test():
        container = app.query_one("#container", Container)
        assert [label.id for label in container.query(Label)] == [
            "l3",
            "l1",
            "l4",
            "l2",
        ]
        # Without a key, the sort order is the order children were instantiated
        container.sort_children()
        assert [label.id for label in container.query(Label)] == [
            "l3",
            "l1",
            "l4",
            "l2",
        ]
        container.sort_children(reverse=True)
        assert [label.id for label in container.query(Label)] == [
            "l2",
            "l4",
            "l1",
            "l3",
        ]


def test_bad_widget_name_raised() -> None:
    """Ensure error is raised when bad class names are used for widgets."""

    with pytest.raises(BadWidgetName):

        class lowercaseWidget(Widget):
            pass


def test_lazy_loading() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/5077

    Check that the lazy loading magic doesn't break attribute access.

    """

    with pytest.raises(ImportError):
        from textual.widgets import Foo  # nopycln: import

    from textual import widgets
    from textual.widgets import Label

    assert not hasattr(widgets, "foo")
    assert not hasattr(widgets, "bar")
    assert hasattr(widgets, "Label")


async def test_of_type() -> None:
    class MyApp(App):
        def compose(self) -> ComposeResult:
            for ordinal in range(5):
                yield Label(f"Item {ordinal}")

    app = MyApp()
    async with app.run_test():
        labels = list(app.query(Label))
        assert labels[0].first_of_type
        assert not labels[0].last_of_type
        assert labels[0].first_child
        assert not labels[0].last_child
        assert labels[0].is_odd
        assert not labels[0].is_even

        assert not labels[1].first_of_type
        assert not labels[1].last_of_type
        assert not labels[1].first_child
        assert not labels[1].last_child
        assert not labels[1].is_odd
        assert labels[1].is_even

        assert not labels[2].first_of_type
        assert not labels[2].last_of_type
        assert not labels[2].first_child
        assert not labels[2].last_child
        assert labels[2].is_odd
        assert not labels[2].is_even

        assert not labels[3].first_of_type
        assert not labels[3].last_of_type
        assert not labels[3].first_child
        assert not labels[3].last_child
        assert not labels[3].is_odd
        assert labels[3].is_even

        assert not labels[4].first_of_type
        assert labels[4].last_of_type
        assert not labels[4].first_child
        assert labels[4].last_child
        assert labels[4].is_odd
        assert not labels[4].is_even


async def test_click_line_api_border():
    """Regression test for https://github.com/Textualize/textual/issues/5634"""

    class MyApp(App):
        def compose(self) -> ComposeResult:
            self.my_log = Log()
            self.my_log.styles.border = ("round", "white")
            yield self.my_log

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("Log", (10, 0))
