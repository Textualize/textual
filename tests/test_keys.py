import pytest

from textual.keys import (
    _get_suggested_binding_key,
)

suggested_binding_keys = [
    ("a", "a"),
    (".", "full_stop"),
    ("#", "number_sign"),
    ("+", "plus"),
]


@pytest.mark.parametrize("key,expected_suggestion", suggested_binding_keys)
def test_suggested_binding_key(key, expected_suggestion):
    suggestion = _get_suggested_binding_key(key)
    assert suggestion == expected_suggestion
