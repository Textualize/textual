from functools import partial

from textual._callback import count_parameters


def test_functions() -> None:
    """Test count parameters of functions."""

    def foo(): ...
    def bar(a): ...
    def baz(a, b): ...

    # repeat to allow for caching
    for _ in range(3):
        assert count_parameters(foo) == 0
        assert count_parameters(bar) == 1
        assert count_parameters(baz) == 2


def test_methods() -> None:
    """Test count parameters of methods."""

    class Foo:
        def foo(self): ...
        def bar(self, a): ...
        def baz(self, a, b): ...

    foo = Foo()

    # repeat to allow for caching
    for _ in range(3):
        assert count_parameters(foo.foo) == 0
        assert count_parameters(foo.bar) == 1
        assert count_parameters(foo.baz) == 2


def test_partials() -> None:
    """Test count parameters of partials."""

    class Foo:
        def method(self, a, b, c, d): ...

    foo = Foo()

    partial0 = partial(foo.method)
    partial1 = partial(foo.method, 10)
    partial2 = partial(foo.method, b=10, c=20)

    for _ in range(3):
        assert count_parameters(partial0) == 4
        assert count_parameters(partial0) == 4

        assert count_parameters(partial1) == 3
        assert count_parameters(partial1) == 3

        assert count_parameters(partial2) == 2
        assert count_parameters(partial2) == 2
