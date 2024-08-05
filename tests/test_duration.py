import pytest

from textual._duration import DurationParseError, _duration_as_seconds


def test_parse() -> None:
    assert _duration_as_seconds("30") == 30.0
    assert _duration_as_seconds("30s") == 30.0
    assert _duration_as_seconds("30000ms") == 30.0
    assert _duration_as_seconds("0.5") == 0.5
    assert _duration_as_seconds("0.5s") == 0.5
    assert _duration_as_seconds("500ms") == 0.5

    with pytest.raises(DurationParseError):
        _duration_as_seconds("300x")
