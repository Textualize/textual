import pytest

from textual._binary_encode import DecodeError, dump, load


@pytest.mark.parametrize(
    "data",
    [
        None,
        False,
        True,
        -10,
        -1,
        0,
        1,
        100,
        "",
        "💩",
        "Hello",
        b"World",
        b"",
        [],
        (),
        [None],
        [1, 2, 3],
        (0, "foo"),
        (1, "foo"),
        (0, ""),
        ("", "💩", "💩💩"),
        (""),
        ["hello", "world"],
        ["hello", b"world"],
        ("hello", "world"),
        ("hello", b"world"),
        ("foo", "bar", "baz"),
        ("foo " * 1000, "bar " * 100, "baz " * 500),
        (1, "foo", "bar", "baz"),
        {},
        {"foo": "bar"},
        {"foo": "bar", b"egg": b"baz"},
        {"foo": "bar", b"egg": b"baz", "list_of_things": [1, 2, 3, "Paul", "Jessica"]},
        [{}],
        [[1]],
        [(1, 2), (3, 4)],
    ],
)
def test_round_trip(data: object) -> None:
    """Test the data may be encoded then decoded"""
    encoded = dump(data)
    assert isinstance(encoded, bytes)
    decoded = load(encoded)
    assert data == decoded


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"100:hello",
        b"i",
        b"i1",
        b"i10",
        b"li1e",
        b"x100",
    ],
)
def test_bad_encoding(data: bytes) -> None:
    with pytest.raises(DecodeError):
        load(data)


@pytest.mark.parametrize(
    "data",
    [
        set(),
        float,
        ...,
        [float],
    ],
)
def test_dump_invalid_type(data):
    with pytest.raises(TypeError):
        dump(data)


def test_load_wrong_type():
    with pytest.raises(TypeError):
        load(None)
    with pytest.raises(TypeError):
        load("foo")
