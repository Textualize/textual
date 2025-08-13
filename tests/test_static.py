from textual.content import Content
from textual.widgets import Static


def test_content_property():
    static = Static()
    assert static.content == ""
    static.content = "Foo"
    assert static.content == "Foo"
    assert isinstance(static.content, str)
    assert static.visual == "Foo"
    assert isinstance(static.visual, Content)

    static.update("Hello")
    assert static.content == "Hello"
    assert isinstance(static.content, str)
    assert static.visual == "Hello"
    assert isinstance(static.visual, Content)
