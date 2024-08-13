import pytest

from textual._binary_encode import DecodeError, dump, load


@pytest.mark.parametrize(
    "data",
    [
        False,
        True,
        -10,
        -1,
        0,
        1,
        100,
        "",
        "Hello",
        b"World",
        b"",
        [],
        (),
        [1, 2, 3],
        ["hello", "world"],
        ["hello", b"world"],
        ("hello", "world"),
        ("hello", b"world"),
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
