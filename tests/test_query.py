from textual.css.query import DOMQuery
from textual.dom import DOMNode


def test_query():
    class Widget(DOMNode):
        pass

    class View(DOMNode):
        pass

    class App(DOMNode):
        pass

    app = App()
    main_view = View(id="main")
    help_view = View(id="help")
    app.add_child(main_view)
    app.add_child(help_view)

    widget1 = Widget(id="widget1")
    widget2 = Widget(id="widget2")
    sidebar = Widget(id="sidebar")
    sidebar.add_class("float")

    helpbar = Widget(id="helpbar")
    helpbar.add_class("float")

    main_view.add_child(widget1)
    main_view.add_child(widget2)
    main_view.add_child(sidebar)

    sub_view = View(id="sub")
    sub_view.add_class("-subview")
    main_view.add_child(sub_view)

    tooltip = Widget(id="tooltip")
    tooltip.add_class("float", "transient")
    sub_view.add_child(tooltip)

    help = Widget(id="markdown")
    help_view.add_child(help)
    help_view.add_child(helpbar)

    # repeat tests to account for caching
    for repeat in range(3):
        assert list(app.query("Frob")) == []
        assert list(app.query(".frob")) == []
        assert list(app.query("#frob")) == []

        assert list(app.query("App")) == [app]
        assert list(app.query("#main")) == [main_view]
        assert list(app.query("View#main")) == [main_view]
        assert list(app.query("#widget1")) == [widget1]
        assert list(app.query("#widget2")) == [widget2]
        assert list(app.query("Widget.float")) == [sidebar, tooltip, helpbar]
        assert list(app.query("Widget.float.transient")) == [tooltip]

        assert list(app.query("App > View")) == [main_view, help_view]
        assert list(app.query("App > View#help")) == [help_view]

        assert list(app.query("#help *")) == [help, helpbar]
