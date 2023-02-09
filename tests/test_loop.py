from textual._loop import loop_first, loop_first_last, loop_last


def test_loop_first():
    assert list(loop_first([])) == []
    iterable = loop_first(["apples", "oranges", "pears", "lemons"])
    assert next(iterable) == (True, "apples")
    assert next(iterable) == (False, "oranges")
    assert next(iterable) == (False, "pears")
    assert next(iterable) == (False, "lemons")


def test_loop_last():
    assert list(loop_last([])) == []
    iterable = loop_last(["apples", "oranges", "pears", "lemons"])
    assert next(iterable) == (False, "apples")
    assert next(iterable) == (False, "oranges")
    assert next(iterable) == (False, "pears")
    assert next(iterable) == (True, "lemons")


def test_loop_first_last():
    assert list(loop_first_last([])) == []
    iterable = loop_first_last(["apples", "oranges", "pears", "lemons"])
    assert next(iterable) == (True, False, "apples")
    assert next(iterable) == (False, False, "oranges")
    assert next(iterable) == (False, False, "pears")
    assert next(iterable) == (False, True, "lemons")
