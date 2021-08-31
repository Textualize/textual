from textual.case import camel_to_snake


def test_camel_to_snake():
    assert camel_to_snake("FooBar") == "foo_bar"
