from textual._loop import loop_first, loop_first_last, loop_from_index, loop_last


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


def test_loop_from_index():
    assert list(loop_from_index("abcdefghij", 3)) == [
        (4, "e"),
        (5, "f"),
        (6, "g"),
        (7, "h"),
        (8, "i"),
        (9, "j"),
        (0, "a"),
        (1, "b"),
        (2, "c"),
        (3, "d"),
    ]

    assert list(loop_from_index("abcdefghij", 3, direction=-1)) == [
        (2, "c"),
        (1, "b"),
        (0, "a"),
        (9, "j"),
        (8, "i"),
        (7, "h"),
        (6, "g"),
        (5, "f"),
        (4, "e"),
        (3, "d"),
    ]

    assert list(loop_from_index("abcdefghij", 3, wrap=False)) == [
        (4, "e"),
        (5, "f"),
        (6, "g"),
        (7, "h"),
        (8, "i"),
        (9, "j"),
    ]
