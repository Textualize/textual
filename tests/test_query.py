import pytest

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import InvalidQueryFormat, NoMatches, TooManyMatches, WrongType
from textual.widget import Widget


def test_query():
    class View(Widget):
        pass

    class View2(View):
        pass

    class App(Widget):
        pass

    app = App()
    main_view = View(id="main")
    help_view = View2(id="help")
    app._add_child(main_view)
    app._add_child(help_view)

    widget1 = Widget(id="widget1")
    widget2 = Widget(id="widget2")
    sidebar = Widget(id="sidebar")
    sidebar.add_class("float")

    helpbar = Widget(id="helpbar")
    helpbar.add_class("float")

    main_view._add_child(widget1)
    main_view._add_child(widget2)
    main_view._add_child(sidebar)

    sub_view = View(id="sub")
    sub_view.add_class("-subview")
    main_view._add_child(sub_view)

    tooltip = Widget(id="tooltip")
    tooltip.add_class("float", "transient")
    sub_view._add_child(tooltip)

    help = Widget(id="markdown")
    help_view._add_child(help)
    help_view._add_child(helpbar)

    # repeat tests to account for caching
    for repeat in range(3):
        assert list(app.query("Frob")) == []
        assert list(app.query(".frob")) == []
        assert list(app.query("#frob")) == []

        assert not app.query("NotAnApp")

        assert list(app.query("App")) == []  # Root is not included in queries
        assert list(app.query("#main")) == [main_view]
        assert list(app.query("View#main")) == [main_view]
        assert list(app.query("View2#help")) == [help_view]
        assert list(app.query("#widget1")) == [widget1]
        assert list(app.query("#Widget1")) == []  # Note case.
        assert list(app.query("#widget2")) == [widget2]
        assert list(app.query("#Widget2")) == []  # Note case.

        assert list(app.query("Widget.float")) == [sidebar, tooltip, helpbar]
        assert list(app.query(Widget).filter(".float")) == [sidebar, tooltip, helpbar]
        assert list(
            app.query(Widget)
            .exclude("App")
            .exclude("#sub")
            .exclude("#markdown")
            .exclude("#main")
            .exclude("#help")
            .exclude("#widget1")
            .exclude("#widget2")
        ) == [sidebar, tooltip, helpbar]
        assert list(reversed(app.query("Widget.float"))) == [helpbar, tooltip, sidebar]
        assert list(app.query("Widget.float").results(Widget)) == [
            sidebar,
            tooltip,
            helpbar,
        ]
        assert list(app.query("Widget.float").results()) == [
            sidebar,
            tooltip,
            helpbar,
        ]
        assert list(app.query("Widget.float").results(View)) == []
        assert app.query_one("#widget1") == widget1
        assert app.query_one("#widget1", Widget) == widget1
        with pytest.raises(TooManyMatches):
            _ = app.query_one(Widget)

        assert app.query("Widget.float")[0] == sidebar
        assert app.query("Widget.float")[0:2] == [sidebar, tooltip]

        assert list(app.query("Widget.float.transient")) == [tooltip]

        assert list(app.query("App > View")) == [main_view, help_view]
        assert list(app.query("App > View#help")) == [help_view]
        assert list(app.query("App > View#main .float ")) == [sidebar, tooltip]
        assert list(app.query("View > View")) == [sub_view]

        assert list(app.query("#help *")) == [help, helpbar]
        assert list(app.query("#main *")) == [
            widget1,
            widget2,
            sidebar,
            sub_view,
            tooltip,
        ]

        assert list(app.query("View")) == [main_view, sub_view, help_view]
        assert list(app.query("#widget1, #widget2")) == [widget1, widget2]
        assert list(app.query("#widget1 , #widget2")) == [widget1, widget2]
        assert list(app.query("#widget1, #widget2, App")) == [widget1, widget2]

        assert app.query(".float").first() == sidebar
        assert app.query(".float").last() == helpbar

        with pytest.raises(NoMatches):
            _ = app.query(".no_such_class").first()
        with pytest.raises(NoMatches):
            _ = app.query(".no_such_class").last()

        with pytest.raises(WrongType):
            _ = app.query(".float").first(View)
        with pytest.raises(WrongType):
            _ = app.query(".float").last(View)


def test_query_classes():
    class App(Widget):
        pass

    class ClassTest(Widget):
        pass

    CHILD_COUNT = 100

    # Create a fake app to hold everything else.
    app = App()

    # Now spin up a bunch of children.
    for n in range(CHILD_COUNT):
        app._add_child(ClassTest(id=f"child{n}"))

    # Let's just be 100% sure everything was created fine.
    assert len(app.query(ClassTest)) == CHILD_COUNT

    # Now, let's check there are *no* children with the test class.
    assert len(app.query(".test")) == 0

    # Add the test class to everything and then check again.
    app.query(ClassTest).add_class("test")
    assert len(app.query(".test")) == CHILD_COUNT

    # Remove the test class from everything then try again.
    app.query(ClassTest).remove_class("test")
    assert len(app.query(".test")) == 0

    # Add the test class to everything using set_class.
    app.query(ClassTest).set_class(True, "test")
    assert len(app.query(".test")) == CHILD_COUNT

    # Remove the test class from everything using set_class.
    app.query(ClassTest).set_class(False, "test")
    assert len(app.query(".test")) == 0

    # Add the test class to everything using toggle_class.
    app.query(ClassTest).toggle_class("test")
    assert len(app.query(".test")) == CHILD_COUNT

    # Remove the test class from everything using toggle_class.
    app.query(ClassTest).toggle_class("test")
    assert len(app.query(".test")) == 0


def test_invalid_query():
    class App(Widget):
        pass

    app = App()

    with pytest.raises(InvalidQueryFormat):
        app.query("#3")

    with pytest.raises(InvalidQueryFormat):
        app.query("#foo").exclude("#2")


async def test_universal_selector_doesnt_select_self():
    class ExampleApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                Widget(
                    Widget(),
                    Widget(
                        Widget(),
                    ),
                ),
                Widget(),
                id="root-container",
            )

    app = ExampleApp()
    async with app.run_test():
        container = app.query_one("#root-container", Container)
        query = container.query("*")
        results = list(query.results())
        assert len(results) == 5
        assert not any(node.id == "root-container" for node in results)
