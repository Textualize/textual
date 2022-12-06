import pytest

from textual.keys import (
    _get_key_for_char,
)

char_key_mappings = [
    ("a", "a"),
    (".", "full_stop"),
    ("#", "number_sign"),
]


@pytest.mark.parametrize("char,expected_key", char_key_mappings)
def test_char_key_mapping(char, expected_key):
    key_from_char = _get_key_for_char(char)
    assert key_from_char == expected_key
