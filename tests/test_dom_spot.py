from textual.widget import Widget

class Content(Widget):
    pass

class Body(Widget):
    pass

def test_find_dom_spot():
    screen = Widget(name="Screen")
    header = Widget(name="Header", id="header")
    body   = Body(id="body")
    content = [ Content(id=f"item{n}") for n in range(1000)]
    body._add_children(*content)
    footer = Widget(name="Footer", id="footer")
    screen._add_children(header, body, footer)
    assert list(screen.children) == [header,body,footer]
    assert screen._find_spot(None) == (screen,-1)
    assert screen._find_spot(1) == (screen, 1)
    assert screen._find_spot(body) == screen._find_spot(1)
    assert screen._find_spot("Body") == screen._find_spot(body)
    assert screen._find_spot("#body") == screen._find_spot(1)
