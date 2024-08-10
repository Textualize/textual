import pytest

from textual.css.errors import StyleValueError
from textual.dom import BadIdentifier, DOMNode


def test_display_default():
    node = DOMNode()
    assert node.display is True


@pytest.mark.parametrize(
    "setter_value,style_value",
    [[True, "block"], [False, "none"], ["block", "block"], ["none", "none"]],
)
def test_display_set_bool(setter_value, style_value):
    node = DOMNode()
    node.display = setter_value
    assert node.styles.display == style_value


def test_display_set_invalid_value():
    node = DOMNode()
    with pytest.raises(StyleValueError):
        node.display = "blah"


def test_validate():
    with pytest.raises(BadIdentifier):
        DOMNode(id="23")
    with pytest.raises(BadIdentifier):
        DOMNode(id=".3")
    with pytest.raises(BadIdentifier):
        DOMNode(classes="+2323")
    with pytest.raises(BadIdentifier):
        DOMNode(classes="foo 22")

    node = DOMNode()
    node.add_class("foo")
    with pytest.raises(BadIdentifier):
        node.add_class("1")
    with pytest.raises(BadIdentifier):
        node.remove_class("1")
    with pytest.raises(BadIdentifier):
        node.toggle_class("1")


def test_classes_setter():
    node = DOMNode(classes="foo bar")
    assert node.classes == frozenset({"foo", "bar"})
    node.classes = "baz egg"
    assert node.classes == frozenset({"baz", "egg"})
    node.classes = ""
    assert node.classes == frozenset({})


def test_classes_setter_iterable():
    node = DOMNode(classes="foo bar")
    assert node.classes == frozenset({"foo", "bar"})
    node.classes = "baz", "egg"
    assert node.classes == frozenset({"baz", "egg"})
    node.classes = []
    assert node.classes == frozenset({})


def test_classes_set_classes():
    node = DOMNode(classes="foo bar")
    assert node.classes == frozenset({"foo", "bar"})
    node.set_classes("baz egg")
    assert node.classes == frozenset({"baz", "egg"})
    node.set_classes([])
    assert node.classes == frozenset({})
    node.set_classes(["paul"])
    assert node.classes == frozenset({"paul"})
    with pytest.raises(BadIdentifier):
        node.classes = "foo 25"
    with pytest.raises(BadIdentifier):
        node.classes = ["foo", "25"]


def test_inherited_bindings():
    """Test if binding merging is done correctly when (not) inheriting bindings."""

    class A(DOMNode):
        BINDINGS = [("a", "a", "a")]

    class B(A):
        BINDINGS = [("b", "b", "b")]

    class C(B, inherit_bindings=False):
        BINDINGS = [("c", "c", "c")]

    class D(C, inherit_bindings=False):
        pass

    class E(D):
        BINDINGS = [("e", "e", "e")]

    a = A()
    assert list(a._bindings.key_to_bindings.keys()) == ["a"]

    b = B()
    assert list(b._bindings.key_to_bindings.keys()) == ["a", "b"]

    c = C()
    assert list(c._bindings.key_to_bindings.keys()) == ["c"]

    d = D()
    assert not list(d._bindings.key_to_bindings.keys())

    e = E()
    assert list(e._bindings.key_to_bindings.keys()) == ["e"]


def test__get_default_css():
    class A(DOMNode):
        pass

    class B(A):
        pass

    class C(B):
        DEFAULT_CSS = "C"

    class D(C):
        pass

    class E(D):
        DEFAULT_CSS = "E"

    node = DOMNode()
    node_css = node._get_default_css()
    a = A()
    a_css = a._get_default_css()
    b = B()
    b_css = b._get_default_css()
    c = C()
    c_css = c._get_default_css()
    d = D()
    d_css = d._get_default_css()
    e = E()
    e_css = e._get_default_css()

    # Descendants that don't assign to DEFAULT_CSS don't add new CSS to the stack.
    assert len(node_css) == len(a_css) == len(b_css) == 0
    assert len(c_css) == len(d_css) == 1
    assert len(e_css) == 2

    # Descendants do push the priority of the ancestors' rules down.
    assert c_css[0][2] == d_css[0][2] + 1 == 0

    # The CSS on the stack is the correct one.
    assert e_css[0][1:] == ("E", 0, "E")
    assert e_css[1][1:] == ("C", -2, "C")


def test_component_classes_inheritance():
    """Test if component classes are inherited properly."""

    class A(DOMNode):
        COMPONENT_CLASSES = {"a-1", "a-2"}

    class B(A, inherit_component_classes=False):
        COMPONENT_CLASSES = {"b-1"}

    class C(B):
        COMPONENT_CLASSES = {"c-1", "c-2"}

    class D(C):
        pass

    class E(D):
        COMPONENT_CLASSES = {"e-1"}

    class F(E, inherit_component_classes=False):
        COMPONENT_CLASSES = {"f-1"}

    node = DOMNode()
    node_cc = node._get_component_classes()
    a = A()
    a_cc = a._get_component_classes()
    b = B()
    b_cc = b._get_component_classes()
    c = C()
    c_cc = c._get_component_classes()
    d = D()
    d_cc = d._get_component_classes()
    e = E()
    e_cc = e._get_component_classes()
    f = F()
    f_cc = f._get_component_classes()

    assert node_cc == frozenset()
    assert a_cc == {"a-1", "a-2"}
    assert b_cc == {"b-1"}
    assert c_cc == {"b-1", "c-1", "c-2"}
    assert d_cc == c_cc
    assert e_cc == {"b-1", "c-1", "c-2", "e-1"}
    assert f_cc == {"f-1"}


@pytest.fixture
def search():
    """
        a
       / \
      b   c
     /   / \
    d   e   f
    """
    a = DOMNode(id="a")
    b = DOMNode(id="b")
    c = DOMNode(id="c")
    d = DOMNode(id="d")
    e = DOMNode(id="e")
    f = DOMNode(id="f")

    a._add_child(b)
    a._add_child(c)
    b._add_child(d)
    c._add_child(e)
    c._add_child(f)

    yield a


def test_walk_children_depth(search):
    children = [
        node.id for node in search.walk_children(method="depth", with_self=False)
    ]
    assert children == ["b", "d", "c", "e", "f"]


def test_walk_children_with_self_depth(search):
    children = [
        node.id for node in search.walk_children(method="depth", with_self=True)
    ]
    assert children == ["a", "b", "d", "c", "e", "f"]


def test_walk_children_breadth(search):
    children = [
        node.id for node in search.walk_children(with_self=False, method="breadth")
    ]
    print(children)
    assert children == ["b", "c", "d", "e", "f"]


def test_walk_children_with_self_breadth(search):
    children = [
        node.id for node in search.walk_children(with_self=True, method="breadth")
    ]
    print(children)
    assert children == ["a", "b", "c", "d", "e", "f"]

    children = [
        node.id
        for node in search.walk_children(with_self=True, method="breadth", reverse=True)
    ]

    assert children == ["f", "e", "d", "c", "b", "a"]


@pytest.mark.parametrize(
    "identifier",
    [
        " bad",
        "  terrible  ",
        "worse!  ",
        "&ampersand",
        "amper&sand",
        "ampersand&",
        "2_leading_digits",
        "água",  # water
        "cão",  # dog
        "@'/.23",
    ],
)
def test_id_validation(identifier: str):
    """Regression tests for https://github.com/Textualize/textual/issues/3954."""
    with pytest.raises(BadIdentifier):
        DOMNode(id=identifier)
